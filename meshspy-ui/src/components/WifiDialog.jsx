import { Dialog } from "@headlessui/react";
import { useState } from "react";
import { createWifiYaml } from "../lib/api";

export default function WifiDialog({ open, onClose }) {
  const [form, setForm] = useState({
    ssid: "",
    password: "",
    mqtt_host: "broker.meshspy.lan",
    mqtt_user: "node-wifi",
    mqtt_pass: "",
  });
  const [fileUrl, setFileUrl] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    const res = await createWifiYaml(form);
    const blob = atob(res.content);
    const url = URL.createObjectURL(
      new Blob([blob], { type: "text/yaml" })
    );
    setFileUrl(url);
  }

  return (
    <Dialog open={open} onClose={onClose} className="relative z-20">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="bg-white rounded-xl p-6 w-full max-w-md shadow-lg">
          <Dialog.Title className="text-lg font-semibold mb-4">
            Add Wi‑Fi Node
          </Dialog.Title>

          {fileUrl ? (
            <div className="space-y-4">
              <p className="text-sm">
                YAML generated. Copy it to <code>/config/wifi.yaml</code>{" "}
                on the SD card, then reboot the radio.
              </p>
              <a
                href={fileUrl}
                download="wifi.yaml"
                className="px-4 py-2 rounded bg-meshtastic text-white text-sm"
              >
                Download wifi.yaml
              </a>
              <button
                onClick={() => {
                  setFileUrl(null);
                  onClose();
                }}
                className="text-sm text-gray-600 underline"
              >
                Close
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-3">
              {[
                ["ssid", "Wi‑Fi SSID"],
                ["password", "Wi‑Fi Password"],
                ["mqtt_host", "MQTT Host"],
                ["mqtt_user", "MQTT User"],
                ["mqtt_pass", "MQTT Password"],
              ].map(([k, label]) => (
                <input
                  key={k}
                  type="text"
                  required
                  placeholder={label}
                  value={form[k]}
                  onChange={(e) =>
                    setForm({ ...form, [k]: e.target.value })
                  }
                  className="w-full px-3 py-2 rounded border"
                />
              ))}
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-3 py-1 rounded text-sm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1 rounded bg-meshtastic text-white text-sm"
                >
                  Generate
                </button>
              </div>
            </form>
          )}
        </Dialog.Panel>
      </div>
    </Dialog>
  );
}
