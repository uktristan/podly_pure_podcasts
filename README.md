<h2 align="center">
<img width="50%" src="src/app/static/images/logos/logo_with_text.png" />

</h2>

<p align="center">
<p align="center">Ad-block for podcasts. Create an ad-free RSS feed.</p>
<p align="center">
  <a href="https://discord.gg/FRB98GtF6N" target="_blank">
      <img src="https://img.shields.io/badge/discord-join-blue.svg?logo=discord&logoColor=white" alt="Discord">
  </a>
</p>

## Overview

Podly uses Whisper and Chat GPT to remove ads from podcasts.

Here's how it works:

- You request an episode
- Podly downloads the requested episode
- Whisper transcribes the episode
- Chat GPT labels ad segments
- Podly removes the ad segments
- Podly delivers the ad-free version of the podcast to you


## How To Run

For detailed setup instructions, see our [beginner's guide](docs/how_to_run_beginners.md).

### Quick Start - No Docker

1. Install dependencies:
   ```shell
   # Install ffmpeg
   sudo apt install ffmpeg  # Ubuntu/Debian
   # or
   brew install ffmpeg      # macOS
   
   # Install Python and Node.js dependencies
   pip install pipenv
   ```

2. Set up configuration:
   ```shell
   # Copy example config and edit
   cp config/config.yml.example config/config.yml
   # Edit config.yml and update llm_api_key with your key
   ```

3. Run Podly:
   ```shell
   # Make script executable
   chmod +x run_podly.sh
   
   # Start Podly (interactive mode)
   ./run_podly.sh
   
   # Or start in background mode
   ./run_podly.sh -b
   ```

The script will automatically:
- Set up Python virtual environment
- Install frontend dependencies
- Configure environment variables from config.yml
- Start both backend and frontend servers

### Quick Start - With Docker

1. Set up your configuration:
   ```bash
   cp config/config.yml.example config/config.yml
   # Edit config.yml with your settings
   ```

2. Run Podly with Docker:
   ```bash
   # Make the script executable first
   chmod +x run_podly_docker.sh
   ./run_podly_docker.sh
   ```

   This will automatically detect if you have an NVIDIA GPU and use it for acceleration.


### Manual Setup

If you prefer to run components separately:

1. Install Python dependencies:
   ```shell
   pipenv --python 3.11
   pipenv install
   ```

2. Install frontend dependencies:
   ```shell
   cd frontend
   npm install
   cd ..
   ```

3. Set up environment variables:
   ```shell
   # Set API URL based on your config.yml
   export VITE_API_URL="http://localhost:5002"  # or your server URL
   ```

4. Start backend:
   ```shell
   pipenv run python src/main.py
   ```

5. Start frontend (in another terminal):
   ```shell
   cd frontend
   npm run dev
   ```

The servers will start at http://localhost:5001 (frontend) and http://localhost:5002 (backend) by default.

## Usage

Once the server is running:

1. Open http://localhost:5001 in your web browser
2. Add podcast RSS feeds through the web interface
3. Open your podcast app and subscribe to the Podly endpoint
   - For example, `http://localhost:5001/feed/1`
4. Select an episode & download
5. Wait patiently 😊 (Transcription takes about 1 minute per 15 minutes of podcast on an M3 MacBook)

## Transcription Options

Podly supports multiple options for audio transcription:

1. **Local Whisper (Default)** - Uses OpenAI's Whisper model running locally on your machine

   - See `config/config.yml.example` for configuration
   - Slower but doesn't require an external API (~ 1 minute per 15 minutes of podcast on an M3 MacBook)

2. **OpenAI Hosted Whisper** - Uses OpenAI's hosted Whisper service

   - See `config/config_remote_whisper.yml.example` for configuration
   - Fast and accurate but requires OpenAI API credits

3. **Groq Hosted Whisper** - Uses Groq's hosted Whisper service
   - See `config/config_groq_whisper.yml.example` for configuration
   - Fast and cost-effective alternative to OpenAI

To use Groq for transcription, you'll need a Groq API key. Copy the `config/config_groq_whisper.yml.example` to `config/config.yml` and update the `api_key` field with your Groq API key.

## Public IP / Port Forwarding Setup

Podly can be configured to work with public IP addresses and port forwarding for external access. This is useful when you want to access your Podly instance from outside your local network.

### Quick Setup

Use the automated setup script:

```bash
# Interactive setup wizard
python3 scripts/setup_public_access.py --interactive

# Or configure directly
python3 scripts/setup_public_access.py --host your-public-ip.com
```

### Manual Configuration

1. **Update your config.yml**:
   ```yaml
   # Enable public access features
   enable_public_access: true
   
   # Set your public IP or domain
   public_host: your-public-ip-or-domain.com
   
   # Configure ports (must match your port forwarding)
   backend_server_port: 5002
   frontend_server_port: 5001
   ```

2. **Set up environment variables**:
   ```bash
   export VITE_API_URL=DYNAMIC  # Enables dynamic API URL resolution
   export VITE_BACKEND_PORT=5002
   ```

3. **Configure port forwarding** on your router:
   - Forward port 5001 → your server (frontend)
   - Forward port 5002 → your server (backend)

4. **Run with Docker**:
   ```bash
   docker-compose up --build
   ```

### Access Your Instance

Once configured, access Podly at: `http://your-public-ip:5001`

### Troubleshooting

- **Frontend can't connect to backend**: Check browser console for API errors
- **CORS errors**: Set `CORS_ORIGINS=*` environment variable (less secure)
- **Connection refused**: Verify port forwarding and firewall settings

For detailed setup instructions, see [docs/public_ip_deployment.md](docs/public_ip_deployment.md).

## Remote Setup (Legacy)

For traditional reverse proxy setups, you can configure Podly to work behind a proxy by setting the SERVER in config/config.yml:

```yaml
server: http://my.domain.com
```

Podly supports basic authentication. See below for example setup for `httpd.conf`:

```apache
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so

ProxyPass / http://127.0.0.1:5002/
RequestHeader set X-Forwarded-Proto http
RequestHeader set X-Forwarded-Prefix /

SetEnv proxy-chain-auth On

# auth
<Location />
    AuthName "Registered User"
    AuthType Basic
    AuthUserFile /lib/protected.users
    require valid-user
</Location>
```

Add users by running:

```bash
sudo htpasswd -c /lib/protected.users [username]
```

Some apps will support basic auth in the URL like `http://[username]:[pass]@my.domain.com`

## Ubuntu Service

Add a service file to /etc/systemd/system/podly.service

```
[Unit]
Description=Podly Podcast Service
After=network.target

[Service]
User=yourusername
Group=yourusername
WorkingDirectory=/path/to/your/app
ExecStart=/usr/bin/pipenv run python src/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

enable the service

```
sudo systemctl daemon-reload
sudo systemctl enable podly.service
```

## Database Update

The database should automatically configure & upgrade on launch.

After data model change run:

```
pipenv run flask --app ./src/main.py db migrate -m "[change description]"
```

On next launch the database should update.

## Docker Support

Podly can be run in Docker with support for both NVIDIA GPU and non-NVIDIA environments. Use Docker if you prefer containerized deployment or need GPU acceleration.

### Quick Start with Docker

1. Set up your configuration:
   ```bash
   cp config/config.yml.example config/config.yml
   # Edit config.yml with your settings
   ```

2. Run Podly with Docker:
   ```bash
   # Make the script executable first
   chmod +x run_podly_docker.sh
   ./run_podly_docker.sh
   ```

   This will automatically detect if you have an NVIDIA GPU and use it for acceleration.

### Docker vs Native

- **Use Docker** (`./run_podly_docker.sh`) if you:
  - Want containerized deployment
  - Need GPU acceleration for Whisper
  - Prefer isolated environments
  
- **Use Native** (`./run_podly.sh`) if you:
  - Want faster development iteration
  - Prefer direct access to logs and debugging
  - Don't need GPU acceleration

### Docker Setup Troubleshooting

If you experience Docker build issues, try the test build option to validate your setup:

```bash
./run_podly_docker.sh --test-build
```

### Docker Options

You can use these command-line options with the run script:

```bash
# Force CPU mode even if GPU is available
./run_podly_docker.sh --cpu

# Force GPU mode (will fail if no GPU is available)
./run_podly_docker.sh --gpu

# Only build the Docker image without starting containers
./run_podly_docker.sh --build

# Test if the Docker build works (helpful for troubleshooting)
./run_podly_docker.sh --test-build
```

## FAQ

Q: What does "whitelisted" mean in the UI?

A: It means an episode is eligible for download and ad removal. By default, new episodes are automatically whitelisted (```automatically_whitelist_new_episodes```), and only a limited number of old episodes are auto-whitelisted (```number_of_episodes_to_whitelist_from_archive_of_new_feed```). This helps control costs by limiting how many episodes are processed. You can adjust these settings in your config.yml for more manual control.
  
Q: How can I enable whisper GPU acceleration?

A: There are two ways to enable GPU acceleration:

1. **Using Docker**: 
   - Use the provided Docker setup with `run_podly_docker.sh` which automatically detects and uses NVIDIA GPUs if available
   - You can force GPU mode with `./run_podly_docker.sh --gpu` or force CPU mode with `./run_podly_docker.sh --cpu`

2. **In a local environment**:
   - Install the CUDA version of PyTorch to your virtual environment:
   ```bash
   pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

## Contributing

We welcome contributions to Podly! Here's how you can help:

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/podly.git
   ```
3. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Running Tests

Before submitting a pull request, you can run the same tests that run in CI:

To prep your pipenv environment to run this script, you will need to first run:

```bash
pipenv install --dev
```

Then, to run the checks,

```bash
scripts/ci.sh
```

This will run all the necessary checks including:

- Type checking with mypy
- Code formatting checks
- Unit tests
- Linting

### Pull Request Process

1. Ensure all tests pass locally
2. Update the documentation if needed
3. Create a Pull Request with a clear description of the changes
4. Link any related issues

### Code Style

- We use black for code formatting
- Type hints are required for all new code
- Follow existing patterns in the codebase
