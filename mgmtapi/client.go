package mgmtapi

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	mqttpkg "meshspy/client"
	"meshspy/storage"

	"google.golang.org/protobuf/encoding/protojson"
	latestpb "meshspy/proto/latest/meshtastic"
)

// Client communicates with the management server HTTP API.
type Client struct {
	baseURL   string
	http      *http.Client
	connected bool
}

// NodeRequest represents a node registration request payload.
type NodeRequest struct {
	ID        string  `json:"id"`
	Name      string  `json:"name"`
	Address   string  `json:"address"`
	Latitude  float64 `json:"latitude,omitempty"`
	Longitude float64 `json:"longitude,omitempty"`
	Model     string  `json:"model,omitempty"`
	Firmware  string  `json:"firmware,omitempty"`
	LongName  string  `json:"longName,omitempty"`
	ShortName string  `json:"shortName,omitempty"`
}

// New returns a new API client for the given base URL. If url is empty,
// the returned client will be nil.
func New(url string) *Client {
	if url == "" {
		return nil
	}
	c := &Client{
		baseURL:   strings.TrimRight(url, "/"),
		http:      &http.Client{Timeout: 5 * time.Second},
		connected: true,
	}
	go c.retryLoop()
	return c
}

func (c *Client) ping() error {
	req, err := http.NewRequest(http.MethodGet, c.baseURL+"/nodes", nil)
	if err != nil {
		return err
	}
	resp, err := c.do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}

func (c *Client) retryLoop() {
	ticker := time.NewTicker(5 * time.Minute)
	defer ticker.Stop()
	for range ticker.C {
		if c.connected {
			continue
		}
		if err := c.ping(); err == nil {
			c.connected = true
		}
	}
}

func (c *Client) do(req *http.Request) (*http.Response, error) {
	resp, err := c.http.Do(req)
	if err != nil {
		c.connected = false
		return nil, err
	}
	if resp.StatusCode >= 300 {
		c.connected = false
		return resp, fmt.Errorf("server returned %s", resp.Status)
	}
	c.connected = true
	return resp, nil
}

// SendNode uploads a NodeInfo to the management server.
func (c *Client) SendNode(info *mqttpkg.NodeInfo) error {
	if c == nil || info == nil {
		return nil
	}
	// MeshSpy-Server expects a simplified Node payload
	data := struct {
		ID      string `json:"id"`
		Name    string `json:"name"`
		Address string `json:"address"`
	}{
		ID:      info.ID,
		Name:    info.LongName,
		Address: info.ShortName,
	}
	b, err := json.Marshal(data)
	if err != nil {
		return err
	}
	// The Java server exposes the node endpoint at /nodes
	req, err := http.NewRequest(http.MethodPost, c.baseURL+"/nodes", bytes.NewReader(b))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := c.do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}

// SendCommand sends a command string to the server which will publish it on MQTT.
func (c *Client) SendCommand(cmd string) error {
	if c == nil {
		return nil
	}
	payload := struct {
		Cmd string `json:"cmd"`
	}{Cmd: cmd}
	b, err := json.Marshal(payload)
	if err != nil {
		return err
	}
	req, err := http.NewRequest(http.MethodPost, c.baseURL+"/api/send", bytes.NewReader(b))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := c.do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}

// ListNodes retrieves the known nodes from the server.
func (c *Client) ListNodes() ([]*mqttpkg.NodeInfo, error) {
	if c == nil {
		return nil, nil
	}
	req, err := http.NewRequest(http.MethodGet, c.baseURL+"/nodes", nil)
	if err != nil {
		return nil, err
	}
	resp, err := c.do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	var raw []struct {
		ID      string `json:"id"`
		Name    string `json:"name"`
		Address string `json:"address"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&raw); err != nil {
		return nil, err
	}
	nodes := make([]*mqttpkg.NodeInfo, 0, len(raw))
	for _, n := range raw {
		nodes = append(nodes, &mqttpkg.NodeInfo{
			ID:        n.ID,
			LongName:  n.Name,
			ShortName: n.Address,
		})
	}
	return nodes, nil
}

// RegisterNode sends a node registration request to the server.
func (c *Client) RegisterNode(req *NodeRequest) error {
	if c == nil || req == nil {
		return nil
	}
	b, err := json.Marshal(req)
	if err != nil {
		return err
	}
	httpReq, err := http.NewRequest(http.MethodPost, c.baseURL+"/node-requests", bytes.NewReader(b))
	if err != nil {
		return err
	}
	httpReq.Header.Set("Content-Type", "application/json")
	resp, err := c.do(httpReq)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}

// ListNodeRequests retrieves pending node registration requests.
func (c *Client) ListNodeRequests() ([]NodeRequest, error) {
	if c == nil {
		return nil, nil
	}
	req, err := http.NewRequest(http.MethodGet, c.baseURL+"/node-requests", nil)
	if err != nil {
		return nil, err
	}
	resp, err := c.do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	var list []NodeRequest
	if err := json.NewDecoder(resp.Body).Decode(&list); err != nil {
		return nil, err
	}
	return list, nil
}

// ApproveNodeRequest approves a pending node request by ID.
func (c *Client) ApproveNodeRequest(id string) error {
	if c == nil || id == "" {
		return nil
	}
	url := fmt.Sprintf("%s/node-requests/%s/approve", c.baseURL, id)
	req, err := http.NewRequest(http.MethodPost, url, nil)
	if err != nil {
		return err
	}
	resp, err := c.do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}

// RejectNodeRequest rejects a pending node request by ID.
func (c *Client) RejectNodeRequest(id string) error {
	if c == nil || id == "" {
		return nil
	}
	url := fmt.Sprintf("%s/node-requests/%s", c.baseURL, id)
	req, err := http.NewRequest(http.MethodDelete, url, nil)
	if err != nil {
		return err
	}
	resp, err := c.do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}

// ListPositions retrieves node positions from the server.
func (c *Client) ListPositions(nodeID string) ([]storage.NodePosition, error) {
	if c == nil {
		return nil, nil
	}
	url := c.baseURL + "/api/positions"
	if nodeID != "" {
		url += "?node=" + nodeID
	}
	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		return nil, err
	}
	resp, err := c.do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	var pos []storage.NodePosition
	if err := json.NewDecoder(resp.Body).Decode(&pos); err != nil {
		return nil, err
	}
	return pos, nil
}

// SendTelemetry uploads a Telemetry message to the management server.
func (c *Client) SendTelemetry(t *latestpb.Telemetry) error {
	if c == nil || t == nil {
		return nil
	}
	b, err := protojson.Marshal(t)
	if err != nil {
		return err
	}
	req, err := http.NewRequest(http.MethodPost, c.baseURL+"/api/telemetry", bytes.NewReader(b))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := c.do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}

// SendWaypoint uploads a Waypoint message to the management server.
func (c *Client) SendWaypoint(wp *latestpb.Waypoint) error {
	if c == nil || wp == nil {
		return nil
	}
	b, err := protojson.Marshal(wp)
	if err != nil {
		return err
	}
	req, err := http.NewRequest(http.MethodPost, c.baseURL+"/api/waypoints", bytes.NewReader(b))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := c.do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}

// SendAdmin uploads raw admin payload to the management server encoded as base64.
func (c *Client) SendAdmin(payload []byte) error {
	if c == nil || payload == nil {
		return nil
	}
	data := struct {
		Payload string `json:"payload"`
	}{Payload: base64.StdEncoding.EncodeToString(payload)}
	b, err := json.Marshal(data)
	if err != nil {
		return err
	}
	req, err := http.NewRequest(http.MethodPost, c.baseURL+"/api/admin", bytes.NewReader(b))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := c.do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}

// SendAlert uploads an alert text message to the management server.
func (c *Client) SendAlert(text string) error {
	if c == nil || text == "" {
		return nil
	}
	data := struct {
		Text string `json:"text"`
	}{Text: text}
	b, err := json.Marshal(data)
	if err != nil {
		return err
	}
	req, err := http.NewRequest(http.MethodPost, c.baseURL+"/api/alerts", bytes.NewReader(b))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := c.do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}

// ListBackups fetches stored configuration backups for the node.
func (c *Client) ListBackups(id string) ([]string, error) {
	if c == nil || id == "" {
		return nil, nil
	}
	url := fmt.Sprintf("%s/nodes/%s/backups", c.baseURL, id)
	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		return nil, err
	}
	resp, err := c.do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	var list []string
	if err := json.NewDecoder(resp.Body).Decode(&list); err != nil {
		return nil, err
	}
	return list, nil
}

// AddBackup uploads a new configuration backup for the node.
func (c *Client) AddBackup(id, data string) error {
	if c == nil || id == "" || data == "" {
		return nil
	}
	payload := struct {
		Data string `json:"data"`
	}{Data: data}
	b, err := json.Marshal(payload)
	if err != nil {
		return err
	}
	url := fmt.Sprintf("%s/nodes/%s/backup", c.baseURL, id)
	req, err := http.NewRequest(http.MethodPost, url, bytes.NewReader(b))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := c.do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}

// RestoreBackup uploads configuration data to restore the node.
func (c *Client) RestoreBackup(id, data string) error {
	if c == nil || id == "" || data == "" {
		return nil
	}
	payload := struct {
		Data string `json:"data"`
	}{Data: data}
	b, err := json.Marshal(payload)
	if err != nil {
		return err
	}
	url := fmt.Sprintf("%s/nodes/%s/restore", c.baseURL, id)
	req, err := http.NewRequest(http.MethodPost, url, bytes.NewReader(b))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := c.do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}

// UpdateFirmware records a firmware update request for the node.
func (c *Client) UpdateFirmware(id, version, urlStr string, build bool) error {
	if c == nil || id == "" {
		return nil
	}
	payload := struct {
		Version string `json:"version,omitempty"`
		URL     string `json:"url,omitempty"`
		Build   bool   `json:"build,omitempty"`
	}{Version: version, URL: urlStr, Build: build}
	b, err := json.Marshal(payload)
	if err != nil {
		return err
	}
	url := fmt.Sprintf("%s/nodes/%s/firmware/update", c.baseURL, id)
	req, err := http.NewRequest(http.MethodPost, url, bytes.NewReader(b))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := c.do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}

// GetFirmware retrieves the latest known firmware version for the node.
func (c *Client) GetFirmware(id string) (string, error) {
	if c == nil || id == "" {
		return "", nil
	}
	url := fmt.Sprintf("%s/nodes/%s/firmware", c.baseURL, id)
	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		return "", err
	}
	resp, err := c.do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	b, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}
	return string(bytes.TrimSpace(b)), nil
}

// GetNode retrieves a single node by ID from the server.
func (c *Client) GetNode(id string) (*mqttpkg.NodeInfo, error) {
	if c == nil || id == "" {
		return nil, nil
	}
	url := fmt.Sprintf("%s/nodes/%s", c.baseURL, id)
	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		return nil, err
	}
	resp, err := c.do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	var n struct {
		ID      string `json:"id"`
		Name    string `json:"name"`
		Address string `json:"address"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&n); err != nil {
		return nil, err
	}
	return &mqttpkg.NodeInfo{ID: n.ID, LongName: n.Name, ShortName: n.Address}, nil
}

// ResetNodes removes all nodes from the server while keeping pending requests.
func (c *Client) ResetNodes() error {
	if c == nil {
		return nil
	}
	req, err := http.NewRequest(http.MethodPost, c.baseURL+"/nodes/reset", nil)
	if err != nil {
		return err
	}
	resp, err := c.do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}
