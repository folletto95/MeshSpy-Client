package mgmtapi

import (
	"encoding/base64"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	latestpb "meshspy/proto/latest/meshtastic"
)

func TestSendTelemetry(t *testing.T) {
	var body string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/api/telemetry" {
			t.Fatalf("path %s", r.URL.Path)
		}
		b, _ := io.ReadAll(r.Body)
		body = string(b)
	}))
	defer srv.Close()

	c := New(srv.URL)
	tel := &latestpb.Telemetry{Time: 1}
	if err := c.SendTelemetry(tel); err != nil {
		t.Fatalf("send: %v", err)
	}
	if !strings.Contains(body, "\"time\":1") {
		t.Fatalf("unexpected body %s", body)
	}
}

func TestSendWaypoint(t *testing.T) {
	var path string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		path = r.URL.Path
	}))
	defer srv.Close()
	c := New(srv.URL)
	wp := &latestpb.Waypoint{Name: "here"}
	if err := c.SendWaypoint(wp); err != nil {
		t.Fatalf("send: %v", err)
	}
	if path != "/api/waypoints" {
		t.Fatalf("path %s", path)
	}
}

func TestSendAdmin(t *testing.T) {
	var got string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		b, _ := io.ReadAll(r.Body)
		got = string(b)
	}))
	defer srv.Close()
	c := New(srv.URL)
	if err := c.SendAdmin([]byte{0x01, 0x02}); err != nil {
		t.Fatalf("send: %v", err)
	}
	if !strings.Contains(got, base64.StdEncoding.EncodeToString([]byte{0x01, 0x02})) {
		t.Fatalf("bad body %s", got)
	}
}

func TestSendAlert(t *testing.T) {
	var got string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		b, _ := io.ReadAll(r.Body)
		got = string(b)
	}))
	defer srv.Close()
	c := New(srv.URL)
	if err := c.SendAlert("boom"); err != nil {
		t.Fatalf("send: %v", err)
	}
	if !strings.Contains(got, "boom") {
		t.Fatalf("bad body %s", got)
	}
}

func TestRegisterAndListNodeRequests(t *testing.T) {
	var receivedPath string
	var method string
	var body string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		receivedPath = r.URL.Path
		method = r.Method
		b, _ := io.ReadAll(r.Body)
		body = string(b)
		if r.Method == http.MethodGet {
			w.Header().Set("Content-Type", "application/json")
			io.WriteString(w, `[{"id":"1"}]`)
		}
	}))
	defer srv.Close()

	c := New(srv.URL)
	req := &NodeRequest{ID: "1", Name: "n", Address: "a", Model: "m"}
	if err := c.RegisterNode(req); err != nil {
		t.Fatalf("register: %v", err)
	}
	if receivedPath != "/node-requests" || method != http.MethodPost {
		t.Fatalf("bad request %s %s", method, receivedPath)
	}
	if !strings.Contains(body, "\"id\":\"1\"") {
		t.Fatalf("bad body %s", body)
	}

	// test list
	list, err := c.ListNodeRequests()
	if err != nil {
		t.Fatalf("list: %v", err)
	}
	if len(list) != 1 || list[0].ID != "1" {
		t.Fatalf("unexpected list %+v", list)
	}
}

func TestApproveRejectNodeRequest(t *testing.T) {
	var paths []string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		paths = append(paths, r.Method+" "+r.URL.Path)
	}))
	defer srv.Close()

	c := New(srv.URL)
	if err := c.ApproveNodeRequest("x"); err != nil {
		t.Fatalf("approve: %v", err)
	}
	if err := c.RejectNodeRequest("y"); err != nil {
		t.Fatalf("reject: %v", err)
	}
	if len(paths) != 2 || paths[0] != "POST /node-requests/x/approve" || paths[1] != "DELETE /node-requests/y" {
		t.Fatalf("unexpected paths %v", paths)
	}
}
func TestNodeManagement(t *testing.T) {
	var paths []string
	var bodies []string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		paths = append(paths, r.Method+" "+r.URL.Path)
		b, _ := io.ReadAll(r.Body)
		bodies = append(bodies, string(b))
		if r.Method == http.MethodGet {
			w.Header().Set("Content-Type", "application/json")
			io.WriteString(w, `["one","two"]`)
		}
	}))
	defer srv.Close()
	c := New(srv.URL)
	if _, err := c.ListBackups("n1"); err != nil {
		t.Fatalf("list backups: %v", err)
	}
	if err := c.AddBackup("n1", "cfg"); err != nil {
		t.Fatalf("add backup: %v", err)
	}
	if err := c.RestoreBackup("n1", "cfg"); err != nil {
		t.Fatalf("restore backup: %v", err)
	}
	if err := c.UpdateFirmware("n1", "v1", "", false); err != nil {
		t.Fatalf("firmware: %v", err)
	}
	if _, err := c.GetFirmware("n1"); err != nil {
		t.Fatalf("get firmware: %v", err)
	}
	expected := []string{
		"GET /nodes/n1/backups",
		"POST /nodes/n1/backup",
		"POST /nodes/n1/restore",
		"POST /nodes/n1/firmware/update",
		"GET /nodes/n1/firmware",
	}
	if len(paths) != len(expected) {
		t.Fatalf("paths %v", paths)
	}
	for i, p := range expected {
		if paths[i] != p {
			t.Fatalf("got %s want %s", paths[i], p)
		}
	}
	if !strings.Contains(bodies[1], "cfg") || !strings.Contains(bodies[2], "cfg") {
		t.Fatalf("bad bodies %v", bodies)
	}
}

func TestGetNodeAndReset(t *testing.T) {
	var paths []string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		paths = append(paths, r.Method+" "+r.URL.Path)
		if r.Method == http.MethodGet {
			w.Header().Set("Content-Type", "application/json")
			io.WriteString(w, `{"id":"n1","name":"test","address":"aa"}`)
		}
	}))
	defer srv.Close()

	c := New(srv.URL)
	n, err := c.GetNode("n1")
	if err != nil {
		t.Fatalf("get node: %v", err)
	}
	if n.ID != "n1" || n.LongName != "test" || n.ShortName != "aa" {
		t.Fatalf("unexpected node %+v", n)
	}
	if err := c.ResetNodes(); err != nil {
		t.Fatalf("reset: %v", err)
	}
	expected := []string{"GET /nodes/n1", "POST /nodes/reset"}
	if len(paths) != len(expected) {
		t.Fatalf("paths %v", paths)
	}
	for i, p := range expected {
		if paths[i] != p {
			t.Fatalf("got %s want %s", paths[i], p)
		}
	}
}
