# API Documentation

> **Comprehensive API documentation for the AI Investment Evaluation System**

## 🚀 Quick Start

### Base URL
```
Production: https://api.ai-investment-eval.com/v1
Development: http://localhost:8000/v1
```

### Authentication
All API requests require authentication using JWT tokens:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     https://api.ai-investment-eval.com/v1/evaluations
```

## 📚 API Reference

### Interactive Documentation
- **Swagger UI**: [/docs](http://localhost:8000/docs) - Interactive API explorer
- **ReDoc**: [/redoc](http://localhost:8000/redoc) - Alternative documentation view

### Core Endpoints

#### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/logout` - User logout

#### Documents
- `POST /documents/upload` - Upload documents
- `GET /documents/{id}` - Get document details
- `GET /documents/{id}/content` - Download document
- `DELETE /documents/{id}` - Delete document

#### Evaluations
- `POST /evaluations` - Create new evaluation
- `GET /evaluations/{id}` - Get evaluation details
- `PUT /evaluations/{id}` - Update evaluation
- `GET /evaluations/{id}/report` - Generate report

#### Ventures
- `POST /ventures` - Create venture
- `GET /ventures/{id}` - Get venture details
- `PUT /ventures/{id}` - Update venture
- `GET /ventures` - List ventures

## 📋 Coming Soon

- OpenAPI 3.0 specification files
- SDK documentation for Python and JavaScript
- Webhook configuration guides
- Rate limiting documentation
- Error handling best practices

---

**Last Updated**: [Insert Date]
**API Version**: v1.0.0
