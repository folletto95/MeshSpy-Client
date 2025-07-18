# MeshSpy

MeshSpy reads packets from a Meshtastic device over a serial port and publishes
nodes information to an MQTT broker. The project includes a Go binary and a
Dockerfile to build a minimal container image.

## Requirements

- Go 1.20+ for building locally
- `meshtastic-go` binary available in `/usr/local/bin/meshtastic-go` or built
  using the provided Dockerfile
- A `.env.runtime` file with runtime settings (copy `.env.runtime.example`)

## Building

Create a `.env.build` from the provided example:

```bash
cp .env.build.example .env.build
# edit .env.build with your Docker credentials
```

Then build the image:

```bash
./build.sh
```

To build the container only for a specific platform set the `BUILD_PLATFORMS`
environment variable:

```bash
BUILD_PLATFORMS=linux/amd64 ./build.sh
```

When unset the script builds images for multiple architectures.

Supported platforms:

```
linux/amd64
linux/arm64
linux/arm/v7
linux/arm/v6
linux/386
```
When unset the script builds images for multiple architectures.

### Building binaries

To produce standalone binaries for Linux, Windows and macOS, run:

```bash
./build-binaries.sh
```

The compiled executables will be placed in the `dist/` directory.


## Running

Configure the runtime environment in `.env.runtime` (create it from `.env.runtime.example`). The most important
variable is `SERIAL_PORT` which should point to your Meshtastic serial device.
Then run the container exposing the serial device and MQTT details:

```bash
docker run --device=/dev/ttyACM0 \
  --env-file .env.runtime nicbad/meshspy
```

During start-up the service prints information from `meshtastic-go` and begins

streaming data from the serial port to the configured MQTT topic. When the
`SEND_ALIVE_ON_START` environment variable is set to `true`, the service also
sends a `MeshSpy Alive` message on the configured MQTT topic and to the node
itself using `meshtastic-go message send -m`, so other components can detect that
the service is running and nodes are reached. Set `SEND_WELCOME_ON_START` to
`false` if you do not want the service to send the default welcome text to the
node when starting.

The MQTT client automatically resumes subscriptions when the connection to the
broker is restored.


### `start_meshspy.sh` helper

For a quick start, run the `start_meshspy.sh` script which launches the
container with some default environment variables. The script also loads
additional settings from `.env.runtime` when present:

- `SERIAL_PORT=/dev/ttyACM0`
- `BAUD_RATE=115200`
- `MQTT_BROKER=tcp://smpisa.ddns.net:1883`
- `MQTT_TOPIC=meshspy`
-  (avoid wildcards here, as publishing to topics like `mesh/#` is not supported)
- `MQTT_CLIENT_ID=meshspy-kali`
- `MQTT_USER` and `MQTT_PASS` can be set in `.env.runtime` when the broker requires authentication
- `SEND_ALIVE_ON_START=true`
  (set to `false` if you do **not** want the service to send and log a `MeshSpy Alive`
  message on start-up)
- `SEND_WELCOME_ON_START=true`
  (set to `false` to suppress the welcome text message sent to the node when the
  service starts)
- `NODE_DB_PATH=nodes.db`
  (location of the SQLite database that stores node information. When unset the
  file `nodes.db` is created in the working directory &ndash; `/app/nodes.db`
  inside the container. Set this to an absolute path such as
`/app/data/nodes.db` to persist the database in a mounted host volume.)
 - `MGMT_SERVER_URL=http://localhost:8081/api`
   (when set, node information, telemetry and waypoints are forwarded to the
   management server running at this URL)

The helper sets `SEND_ALIVE_ON_START` and `SEND_WELCOME_ON_START` so the service
announces itself and sends a welcome message when launched.

Start the container using the defaults:

```bash
./start_meshspy.sh
```

Use `--clean` to remove and re-pull the image before starting and `--log` to
periodically show container logs:

```bash
./start_meshspy.sh --clean
./start_meshspy.sh --log
```

Both options can be combined if required.

The service stores information about all discovered nodes in a SQLite database.
By default this file is `nodes.db` in the working directory (`/app/nodes.db`
inside the container). Set the `NODE_DB_PATH` environment variable to point to a
different location, for example `/app/data/nodes.db` when you mount a volume on
the host. Each time a
`NodeInfo` protobuf message is received it is converted and inserted or updated
in this database so that external tools can inspect the mesh topology.

### `start_berry5.sh` helper

Owners of a Raspberry&nbsp;Pi&nbsp;5 can use the `start_berry5.sh` script. It
launches the container for the arm64 architecture and stores the node database
in the `meshspy_data` directory on the host. The helper also reads
configuration from `.env.runtime` if available.

Start it with the defaults:

```bash
./start_berry5.sh
```

As with the generic helper you can combine `--clean` and `--log` to refresh the
image and continuously follow the logs.

## Web Application

A simple web interface lives in `cmd/webapp`. It serves an HTML page and
forwards MQTT messages over WebSockets. Messages typed in the page are
published over MQTT and delivered to the mesh as text packets. Run it with Go:

```bash
go run ./cmd/webapp
```

The application reads the same `.env.runtime` file used by `meshspy` (create this from `.env.runtime.example`). Set
`WEB_PORT` to change the listening port (default `8080`) and open your browser
to `http://localhost:8080`.

## Simple Message Board

For a minimal example that does not rely on MQTT, a tiny in-memory
message board is available in `cmd/messagesapp`:

```bash
go run ./cmd/messagesapp
```

Visit `http://localhost:8080` and post messages through the form to see
them listed on the page.

## API

The client interacts with the management server via HTTP. When the server is not
reachable MeshSpy retries the connection every five minutes until it succeeds.
The server exposes the following JSON endpoints, mirrored from the
[MeshSpy-Server project](https://github.com/folletto95/MeshSpy-Server):

### Node endpoints

* `GET /nodes` – list approved nodes
* `GET /nodes/{id}` – retrieve a single node
* `POST /nodes` – register a node and receive `201 Created` or `202 Accepted`
* `POST /nodes/reset` – remove all nodes while keeping pending requests

### Client endpoints

Endpoints for local clients physically connected via USB:

* `GET /clients` – list connected clients
* `POST /clients` – register a new client using the same payload as `POST /nodes` with `"client": true`
* `POST /clients/reset` – remove all stored clients
* `GET /client-requests` – list pending client registration requests
* `POST /client-requests` – create a new client request
* `POST /client-requests/{id}/approve` – approve a pending client
* `DELETE /client-requests/{id}` – reject a client request
* `POST /clients/{id}/data` – send arbitrary data from the client
* `GET /clients/{id}/data` – list all received data for the client

### Node management

* `GET /nodes/{id}/backups` – list stored configuration backups
* `POST /nodes/{id}/backup` – upload a new configuration backup
* `POST /nodes/{id}/restore` – restore a configuration from provided data
* `POST /nodes/{id}/firmware/update` – record a firmware update request
* `GET /nodes/{id}/firmware` – latest known firmware version

### Registration requests

* `GET /node-requests` – list pending node registrations
* `POST /node-requests` – create a new request including `model`, `firmware`,
  `longName` and `shortName`
* `POST /node-requests/{id}/approve` – approve a request
* `DELETE /node-requests/{id}` – reject and delete a request

Additional endpoints handle telemetry, waypoints, admin payloads and alerts:
`POST /api/telemetry`, `POST /api/waypoints`, `POST /api/admin` and
`POST /api/alerts`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
