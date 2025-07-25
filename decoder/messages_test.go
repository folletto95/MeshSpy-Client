package decoder

import (
	"bytes"
	"testing"

	"google.golang.org/protobuf/proto"
	pb "meshspy/proto/latest/meshtastic"
)

func TestDecodeText(t *testing.T) {
	d := &pb.Data{
		Portnum: pb.PortNum_TEXT_MESSAGE_APP,
		Payload: []byte("hello"),
	}
	mp := &pb.MeshPacket{PayloadVariant: &pb.MeshPacket_Decoded{Decoded: d}}
	fr := &pb.FromRadio{PayloadVariant: &pb.FromRadio_Packet{Packet: mp}}
	data, err := proto.Marshal(fr)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	txt, err := DecodeText(data, "latest")
	if err != nil {
		t.Fatalf("decode failed: %v", err)
	}
	if txt != "hello" {
		t.Fatalf("unexpected text %q", txt)
	}
}

func TestDecodeTextFramedV21(t *testing.T) {
	d := &pb.Data{
		Portnum: pb.PortNum_TEXT_MESSAGE_APP,
		Payload: []byte("hi"),
	}
	mp := &pb.MeshPacket{PayloadVariant: &pb.MeshPacket_Decoded{Decoded: d}}
	fr := &pb.FromRadio{PayloadVariant: &pb.FromRadio_Packet{Packet: mp}}
	payload, err := proto.Marshal(fr)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	header := []byte{0x44, 0x03, byte(len(payload) >> 8), byte(len(payload))}
	frame := append(header, payload...)
	txt, err := DecodeText(frame, "2.1")
	if err != nil {
		t.Fatalf("decode failed: %v", err)
	}
	if txt != "hi" {
		t.Fatalf("unexpected text %q", txt)
	}
}

func TestDecodeTelemetry(t *testing.T) {
	tm := &pb.Telemetry{
		Time:    12345,
		Variant: &pb.Telemetry_DeviceMetrics{DeviceMetrics: &pb.DeviceMetrics{}},
	}
	payload, err := proto.Marshal(tm)
	if err != nil {
		t.Fatalf("marshal telemetry: %v", err)
	}
	d := &pb.Data{
		Portnum: pb.PortNum_TELEMETRY_APP,
		Payload: payload,
	}
	mp := &pb.MeshPacket{PayloadVariant: &pb.MeshPacket_Decoded{Decoded: d}}
	fr := &pb.FromRadio{PayloadVariant: &pb.FromRadio_Packet{Packet: mp}}
	data, err := proto.Marshal(fr)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	dec, err := DecodeTelemetry(data, "latest")
	if err != nil {
		t.Fatalf("decode failed: %v", err)
	}
	if dec.GetTime() != tm.GetTime() {
		t.Fatalf("unexpected time %d", dec.GetTime())
	}
}

func TestDecodeTelemetryFramedV21(t *testing.T) {
	tm := &pb.Telemetry{
		Time:    777,
		Variant: &pb.Telemetry_DeviceMetrics{DeviceMetrics: &pb.DeviceMetrics{}},
	}
	payload, err := proto.Marshal(tm)
	if err != nil {
		t.Fatalf("marshal telemetry: %v", err)
	}
	d := &pb.Data{Portnum: pb.PortNum_TELEMETRY_APP, Payload: payload}
	mp := &pb.MeshPacket{PayloadVariant: &pb.MeshPacket_Decoded{Decoded: d}}
	fr := &pb.FromRadio{PayloadVariant: &pb.FromRadio_Packet{Packet: mp}}
	data, err := proto.Marshal(fr)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	header := []byte{0x44, 0x03, byte(len(data) >> 8), byte(len(data))}
	frame := append(header, data...)
	dec, err := DecodeTelemetry(frame, "2.1")
	if err != nil {
		t.Fatalf("decode failed: %v", err)
	}
	if dec.GetTime() != tm.GetTime() {
		t.Fatalf("unexpected time %d", dec.GetTime())
	}
}

func TestDecodeWaypoint(t *testing.T) {
	wp := &pb.Waypoint{Id: 1, Name: "home"}
	payload, err := proto.Marshal(wp)
	if err != nil {
		t.Fatalf("marshal waypoint: %v", err)
	}
	d := &pb.Data{Portnum: pb.PortNum_WAYPOINT_APP, Payload: payload}
	mp := &pb.MeshPacket{PayloadVariant: &pb.MeshPacket_Decoded{Decoded: d}}
	fr := &pb.FromRadio{PayloadVariant: &pb.FromRadio_Packet{Packet: mp}}
	data, err := proto.Marshal(fr)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	dec, err := DecodeWaypoint(data, "latest")
	if err != nil {
		t.Fatalf("decode failed: %v", err)
	}
	if dec.GetId() != wp.GetId() {
		t.Fatalf("unexpected id %d", dec.GetId())
	}
}

func TestDecodeAdmin(t *testing.T) {
	payload := []byte{0x01, 0x02}
	d := &pb.Data{Portnum: pb.PortNum_ADMIN_APP, Payload: payload}
	mp := &pb.MeshPacket{PayloadVariant: &pb.MeshPacket_Decoded{Decoded: d}}
	fr := &pb.FromRadio{PayloadVariant: &pb.FromRadio_Packet{Packet: mp}}
	data, err := proto.Marshal(fr)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	dec, err := DecodeAdmin(data, "latest")
	if err != nil {
		t.Fatalf("decode failed: %v", err)
	}
	if !bytes.Equal(dec, payload) {
		t.Fatalf("unexpected payload %v", dec)
	}
}

func TestDecodeAlert(t *testing.T) {
	d := &pb.Data{Portnum: pb.PortNum_ALERT_APP, Payload: []byte("boom")}
	mp := &pb.MeshPacket{PayloadVariant: &pb.MeshPacket_Decoded{Decoded: d}}
	fr := &pb.FromRadio{PayloadVariant: &pb.FromRadio_Packet{Packet: mp}}
	data, err := proto.Marshal(fr)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	txt, err := DecodeAlert(data, "latest")
	if err != nil {
		t.Fatalf("decode failed: %v", err)
	}
	if txt != "boom" {
		t.Fatalf("unexpected text %q", txt)
	}
}
