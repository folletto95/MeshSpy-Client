package decoder

import (
	"fmt"

	"google.golang.org/protobuf/proto"
	latestpb "meshspy/proto/latest/meshtastic"
)

// DecodeMyInfo decodes a protobuf blob into a MyNodeInfo message.
func DecodeMyInfo(data []byte, version string) (*latestpb.MyNodeInfo, error) {
	if len(data) >= headerLen &&
		((data[0] == start1 && data[1] == start2) ||
			(data[0] == start1v21 && data[1] == start2v21)) {
		l := int(data[2])<<8 | int(data[3])
		if len(data) >= headerLen+l {
			data = data[headerLen : headerLen+l]
		} else {
			return nil, fmt.Errorf("incomplete frame")
		}
	}
	switch version {
	case "", "latest", "2.1":
		var fr latestpb.FromRadio
		if err := proto.Unmarshal(data, &fr); err == nil && fr.GetMyInfo() != nil {
			return fr.GetMyInfo(), nil
		}
		var mi latestpb.MyNodeInfo
		if err := proto.Unmarshal(data, &mi); err == nil && mi.MyNodeNum != 0 {
			return &mi, nil
		}
		return nil, fmt.Errorf("not a MyNodeInfo message")
	default:
		return nil, fmt.Errorf("unsupported proto version: %s", version)
	}
}
