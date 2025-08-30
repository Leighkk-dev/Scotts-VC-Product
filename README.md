# AI Investment Evaluation System

> **Sophisticated AI-powered investment evaluation platform for venture capital analysis**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18+](https://img.shields.io/badge/react-18+-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)](https://fastapi.tiangolo.com/)

## 🎯 Project Overview

The AI Investment Evaluation System is a comprehensive platform that analyzes venture business models and provides probability-based investment recommendations with human oversight capabilities. Built for Australian VCs with plans to expand across Asia-Pacific markets.

### Key Features

- **🤖 AI-Powered Analysis**: Advanced NLP processing of pitch decks, financials, and business plans
- **📊 Multi-Dimensional Scoring**: Comprehensive risk assessment across financial, market, team, and product dimensions
- **👥 Human-in-the-Loop**: Interactive dashboard with expert override capabilities
- **📈 Probability-Based Recommendations**: Statistical confidence intervals and risk analysis
- **🏛️ Regulatory Compliance**: ASIC/ASX compliant reporting and audit trails
- **📱 Professional Interface**: Intuitive dashboard with comparative analysis tools

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Docker & Docker Compose (recommended)

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd ai-investment-evaluation

# Start with Docker Compose (recommended)
docker-compose up -d

# Or manual setup
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
npm start
```

### Access Points

- **Frontend Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:3000/admin

## 📋 Project Status

**Current Phase**: Foundation Setup (Week 1 of 6)

### Sprint Progress

- [x] Project initialization and documentation
- [ ] Database schema implementation
- [ ] Basic authentication system
- [ ] Document upload infrastructure
- [ ] Core API endpoints

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed sprint timeline and milestones.

## 🏗️ Architecture

### Technology Stack

**Backend**
- FastAPI + Python 3.11+
- PostgreSQL with SQLAlchemy ORM
- Redis for caching
- Hugging Face Transformers
- scikit-learn, spaCy, pandas

**Frontend**
- React 18+ with TypeScript
- Material-UI components
- Chart.js for visualizations
- React Hook Form

**Infrastructure**
- Docker containerization
- AWS/Digital Ocean deployment
- GitHub Actions CI/CD
- Prometheus + Grafana monitoring

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## 📖 Documentation

- [📋 Requirements](REQUIREMENTS.md) - Functional and technical requirements
- [🏗️ Architecture](ARCHITECTURE.md) - System design and technical architecture
- [📅 Project Plan](PROJECT_PLAN.md) - Development phases and milestones
- [🔧 API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)

## 🎯 Target Market

**Primary**: Australian Venture Capital firms
**Secondary**: Asia-Pacific investment organizations
**Timeline**: 6-week MVP → 12-month growth plan

### Business Model

- **Freemium**: 5 evaluations/month, basic reports
- **Professional**: AUD $497/month, unlimited evaluations
- **Enterprise**: AUD $2,497/month, custom models, API access

## 🔒 Compliance & Security

- Australian Privacy Principles (APP) compliance
- ASIC/ASX regulatory requirements
- End-to-end encryption
- Role-based access control
- Comprehensive audit trails

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- TypeScript for frontend, Python type hints for backend
- 80%+ test coverage required
- ESLint/Prettier for JS, Black/isort for Python
- Feature branches with code reviews

## 📊 Success Metrics

### Technical Targets
- Document processing: <3 minutes per file
- Dashboard load time: <2 seconds
- 99.9% uptime target
- 80% AI accuracy by month 6

### Business Targets
- 50 beta users by month 2
- 70% trial-to-paid conversion
- AUD $15,000 MRR by month 3
- 90%+ customer satisfaction

## 📞 Support

- **Documentation**: Check the `/docs` directory
- **Issues**: Use GitHub Issues for bug reports
- **Discussions**: Use GitHub Discussions for questions
- **Email**: [Your contact email]

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for the Australian VC ecosystem**
