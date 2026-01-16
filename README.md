# ThunderX NDR Solution

<div align="center">

![ThunderX Logo](docs/assets/thunderx-logo.png)

**Next-Generation Network Detection and Response Platform**

*Powered by AI | Built on OpenSearch 3.0 | MCP-Enabled*

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0--alpha-orange.svg)](CHANGELOG.md)

</div>

---

## 🚀 What is ThunderX?

ThunderX is a comprehensive Network Detection and Response (NDR) platform that combines powerful network security monitoring with AI-powered analysis through Model Context Protocol (MCP) integration. Built on OpenSearch 3.0's native MCP server, ThunderX enables natural language threat hunting, automated incident response, and intelligent security analysis.

### Key Features

- 🤖 **AI-Powered Analysis**: Natural language queries, automated threat hunting, intelligent correlation via MCP
- 🔍 **Comprehensive Network Monitoring**: Full packet capture, protocol analysis, intrusion detection
- 📊 **Advanced Visualization**: Real-time dashboards, custom analytics, interactive threat hunting
- 🎯 **Flexible Deployment**: Choose standalone or distributed mode during installation
- 🛡️ **Threat Intelligence**: Automated IOC enrichment, multiple feed support, custom intel sources
- 🔔 **Smart Alerting**: AI-powered correlation, case management, automated response recommendations
- 🐳 **Docker-First**: Containerized architecture for easy deployment and scaling
- 🌐 **Modern Web UI**: Intuitive interface with MCP chat for natural language interaction

---

## 🏗️ Architecture

ThunderX integrates industry-leading open-source tools with custom AI capabilities:

### Core Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Network Analysis** | Protocol analysis and logging | Zeek 6.x |
| **Intrusion Detection** | Signature-based detection | Suricata 7.x |
| **Packet Capture** | Full PCAP storage and search | Arkime |
| **Data Platform** | Search, analytics, and AI | OpenSearch 3.0 |
| **MCP AI Service** | Natural language processing | Python + MCP |
| **Visualization** | Dashboards and analytics | OpenSearch Dashboards |
| **Alert Management** | Correlation and case tracking | Custom service |
| **Threat Intel** | IOC feeds and enrichment | Custom service |
| **Web UI** | User interface | React/TypeScript |
| **API Gateway** | REST API and auth | FastAPI/Python |

### Deployment Modes

#### Standalone Mode
All components run on a single host - perfect for small networks, labs, or getting started.

```
┌─────────────────────────────────────┐
│         ThunderX Standalone         │
├─────────────────────────────────────┤
│  Web UI │ OpenSearch │ Zeek │ ...  │
│           Single Host                │
└─────────────────────────────────────┘
```

#### Distributed Mode
Management node + multiple sensor nodes - scales for enterprise networks.

```
┌──────────────────────┐
│   Management Node    │
│  OpenSearch │ Web UI │
└──────────┬───────────┘
           │
    ───────┼───────
    │              │
┌───▼────┐    ┌───▼────┐
│Sensor 1│    │Sensor 2│
│  Zeek  │    │  Zeek  │
└────────┘    └────────┘
```

---

## ⚡ Quick Start

### Prerequisites

- **OS**: Linux (Ubuntu 22.04+, Debian 12+, RHEL 9+ recommended)
- **Docker**: 24.0+ with Docker Compose
- **Resources (Standalone)**: 16GB RAM, 4 CPU cores, 500GB storage
- **Network**: Interface in promiscuous mode for packet capture

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/thunderx.git
   cd thunderx
   ```

2. **Run the installer**
   ```bash
   sudo ./install.sh
   ```

3. **Follow the interactive prompts**
   - Choose deployment mode (standalone/distributed)
   - Configure network interfaces
   - Set admin credentials
   - Select optional features

4. **Access ThunderX**
   ```
   Web UI: https://your-host-ip
   Default credentials: admin / <password-set-during-install>
   ```

### First Steps

1. **Explore the Dashboard**: View real-time network activity
2. **Try MCP Chat**: Ask "Show me top talkers in the last hour"
3. **Configure Alerts**: Set up notifications for your environment
4. **Start Threat Hunting**: Use AI-guided workflows to investigate

---

## 💬 MCP-Powered AI Features

ThunderX's integration with OpenSearch 3.0's native MCP server enables powerful AI capabilities:

### Natural Language Queries

Ask questions in plain English:

```
"Show me all suspicious DNS queries in the last 24 hours"
"What are the top 10 source IPs by traffic volume?"
"Find connections to known malicious IPs"
"Show me failed SSH login attempts"
```

### AI-Assisted Threat Hunting

- **Automated Hypothesis Generation**: AI suggests what to investigate
- **Intelligent Pivoting**: Automatically correlate related events
- **Pattern Recognition**: Identify anomalies and suspicious behaviors
- **Contextual Analysis**: Understand the full scope of incidents

### Incident Response Recommendations

- **Severity Assessment**: AI-powered threat scoring
- **Containment Suggestions**: Recommended immediate actions
- **Remediation Steps**: Guided response workflows
- **Automated Playbooks**: Execute predefined response procedures

---

## 📖 Documentation

- [Architecture Overview](docs/architecture.md)
- [Installation Guide](docs/installation.md)
- [MCP Integration Guide](docs/mcp-integration.md)
- [User Guide](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Threat Hunting Workflows](docs/threat-hunting.md)
- [Distributed Deployment](docs/distributed-deployment.md)
- [Troubleshooting](docs/troubleshooting.md)

---

## 🔧 Configuration

ThunderX configuration is managed through YAML files:

- `config/thunderx.yml` - Main configuration
- `config/opensearch.yml` - OpenSearch settings
- `config/zeek.yml` - Zeek configuration
- `config/suricata.yml` - Suricata configuration
- `config/threat-intel.yml` - Threat feed settings

See [Configuration Guide](docs/configuration.md) for details.

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

ThunderX is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

ThunderX builds on the excellent work of:

- [OpenSearch](https://opensearch.org/) - Search and analytics platform
- [Zeek](https://zeek.org/) - Network security monitoring
- [Suricata](https://suricata.io/) - IDS/IPS engine
- [Arkime](https://arkime.com/) - Full packet capture
- [Security Onion](https://securityonionsolutions.com/) - Inspiration and best practices
- [Malcolm](https://github.com/cisagov/Malcolm) - Architecture patterns

---

## 📞 Support

- **Documentation**: [docs.thunderx.io](https://docs.thunderx.io)
- **Issues**: [GitHub Issues](https://github.com/yourusername/thunderx/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/thunderx/discussions)
- **Community**: [Discord Server](https://discord.gg/thunderx)

---

<div align="center">

**Built with ❤️ for the security community**

[Website](https://thunderx.io) • [Documentation](https://docs.thunderx.io) • [Community](https://discord.gg/thunderx)

</div>
