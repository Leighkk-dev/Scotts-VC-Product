# AI Investment Evaluation System - Preview Guide

## 🚀 Quick Start Preview

### Prerequisites
- Docker and Docker Compose installed
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Option 1: Full Docker Setup (Recommended)

```bash
# Clone and navigate to the project
cd /path/to/ai-investment-evaluation

# Start all services with Docker Compose
docker compose up -d

# Wait for services to start (about 30-60 seconds)
# Check service status
docker compose ps

# View logs if needed
docker compose logs -f backend
docker compose logs -f frontend
```

**Access Points:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin123)
- **Elasticsearch**: http://localhost:9200

### Option 2: Local Development Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis (via Docker)
docker compose up -d postgres redis

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup (New Terminal)
```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

## 🎯 What You'll See

### 1. Landing/Login Page
- Professional login interface
- Material-UI design with custom theme
- Form validation and error handling
- Registration link for new users

### 2. Registration Page
- Multi-step form with validation
- Password strength requirements
- Real-time form validation
- Success/error feedback

### 3. Dashboard (After Login)
- **Stats Cards**: Total ventures, evaluations, documents, average scores
- **Quick Actions**: Add venture, upload documents, start evaluation
- **Recent Activity**: Timeline of recent system activity
- **Professional Layout**: Sidebar navigation, user profile menu

### 4. Navigation Structure
- **Dashboard**: Overview and quick actions
- **Ventures**: Investment opportunities (placeholder for Phase 2)
- **Documents**: File management (placeholder for Phase 2)
- **Evaluations**: AI analysis results (placeholder for Phase 3)
- **Settings**: User and system settings (placeholder for Phase 4)

### 5. API Documentation
- **Interactive Swagger UI**: http://localhost:8000/docs
- **Authentication Endpoints**: Login, register, refresh, logout
- **User Management**: Profile, preferences
- **Placeholder Endpoints**: Ready for Phase 2 implementation

## 🔧 Testing the System

### 1. User Registration Flow
```bash
# Test user registration via API
curl -X POST "http://localhost:8000/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 2. User Login Flow
```bash
# Test login via API
curl -X POST "http://localhost:8000/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPassword123!"
```

### 3. Frontend Testing
1. Navigate to http://localhost:3000
2. Click "Sign up here" to register a new account
3. Fill in the registration form
4. Login with your credentials
5. Explore the dashboard and navigation

## 📱 Mobile Preview
The system is fully responsive and works on:
- **Desktop**: Full feature set with sidebar navigation
- **Tablet**: Collapsible sidebar, optimized layout
- **Mobile**: Drawer navigation, touch-friendly interface

## 🎨 Design Features

### Visual Elements
- **Professional Color Scheme**: Blue primary, red accent colors
- **Material Design**: Google's Material-UI components
- **Custom Theme**: Branded colors and typography
- **Responsive Layout**: Works on all screen sizes
- **Loading States**: Spinners and progress indicators
- **Error Handling**: User-friendly error messages

### User Experience
- **Intuitive Navigation**: Clear menu structure
- **Form Validation**: Real-time validation with helpful messages
- **Accessibility**: WCAG 2.1 AA compliant
- **Performance**: Optimized loading and caching
- **Security**: JWT tokens, secure authentication

## 🔍 System Health Checks

### Backend Health
```bash
# Check backend health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "service": "ai-investment-evaluation",
  "version": "1.0.0",
  "environment": "development"
}
```

### Database Connection
```bash
# Check if database is accessible
docker compose exec postgres psql -U postgres -d investment_eval -c "\dt"
```

### Frontend Build
```bash
# Test frontend build
cd frontend
npm run build
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Conflicts**
   - Frontend (3000), Backend (8000), PostgreSQL (5432), Redis (6379)
   - Stop conflicting services or change ports in docker-compose.yml

2. **Database Connection Issues**
   - Ensure PostgreSQL container is running: `docker compose ps`
   - Check logs: `docker compose logs postgres`

3. **Frontend Build Issues**
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Check Node.js version: `node --version` (should be 18+)

4. **Backend Import Issues**
   - Activate virtual environment: `source venv/bin/activate`
   - Install dependencies: `pip install -r requirements.txt`

### Getting Help
- Check container logs: `docker compose logs [service-name]`
- View all services: `docker compose ps`
- Restart services: `docker compose restart [service-name]`

## 📊 Preview Summary

### What's Working Now (Phase 1)
✅ **User Authentication**: Registration, login, logout, token refresh  
✅ **Professional UI**: Material-UI dashboard with responsive design  
✅ **Database**: PostgreSQL with complete schema and migrations  
✅ **API Documentation**: Interactive Swagger UI  
✅ **Security**: JWT tokens, password hashing, RBAC foundation  
✅ **Infrastructure**: Docker containerization, CI/CD pipeline  

### Coming in Phase 2
🔄 **Document Processing**: PDF, PPT, Excel, Word file uploads  
🔄 **NLP Pipeline**: Text extraction and entity recognition  
🔄 **Basic Scoring**: Initial investment scoring algorithms  
🔄 **File Management**: Drag-and-drop uploads with progress tracking  

### Coming in Phase 3
🔄 **AI Analysis**: Advanced transformer models and risk assessment  
🔄 **Multi-dimensional Scoring**: Financial, market, team, product scores  
🔄 **Visualization**: Charts, graphs, and interactive dashboards  

---

**Ready to preview?** Follow the setup instructions above and explore the system!
