# 🚀 Render Deployment Guide - Foton aiQMS

This guide will help you deploy your FMEA system with trial limits to Render.

## 📋 Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Your code is already pushed to GitHub
3. **OpenAI API Key**: For AI functionality (optional for basic deployment)

## 🎯 Deployment Steps

### Step 1: Connect GitHub Repository

1. **Login to Render Dashboard**
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Sign in with your GitHub account

2. **Create New Blueprint**
   - Click "New +" button
   - Select "Blueprint"
   - Connect your GitHub repository: `JMSpanoman/fmea-ai`

### Step 2: Deploy Backend Service

1. **Backend will deploy automatically** from your `render.yaml`
   - Service name: `fmea-backend`
   - URL: `https://fmea-backend.onrender.com`
   - Docker build from `./Dockerfile.backend`

2. **Set Environment Variables** (in Render Dashboard):
   - `ENVIRONMENT`: `production` ✅ (already set)
   - `CORS_ORIGINS`: `https://fmea-frontend.onrender.com` ✅ (already set)
   - `DATABASE_URL`: `sqlite:////app/db/fmea.db` ✅ (already set)
   - `SECRET_KEY`: Auto-generated ✅ (already set)
   - `OPENAI_API_KEY`: Set your OpenAI API key here
   - `PORT`: `8000` ✅ (already set)

### Step 3: Deploy Frontend Service

1. **Frontend will deploy automatically** from your `render.yaml`
   - Service name: `fmea-frontend`
   - URL: `https://fmea-frontend.onrender.com`
   - Docker build from `./Dockerfile.frontend`

2. **Set Environment Variables** (in Render Dashboard):
   - `VITE_API_BASE_URL`: `https://fmea-backend.onrender.com` ✅ (already set)
   - `BACKEND_URL`: `https://fmea-backend.onrender.com` ✅ (already set)
   - `NODE_ENV`: `production` ✅ (already set)
   - `PORT`: `80` ✅ (already set)

### Step 4: Configure OpenAI API Key

1. **Get OpenAI API Key**:
   - Go to [platform.openai.com](https://platform.openai.com)
   - Create account or login
   - Go to API Keys section
   - Create new secret key

2. **Set in Render Dashboard**:
   - Go to your backend service
   - Environment tab
   - Add `OPENAI_API_KEY` with your key value
   - Save changes

### Step 5: Verify Deployment

1. **Check Backend Health**:
   - Visit: `https://fmea-backend.onrender.com/health`
   - Should return: `{"status": "healthy"}`

2. **Check Frontend**:
   - Visit: `https://fmea-frontend.onrender.com`
   - Should show login page

3. **Test Login**:
   - Try logging in with: `john@fotonconsulting.com`
   - Should see admin access with unlimited AI generations

## 🔧 Manual Deployment (Alternative)

If you prefer manual deployment:

### Backend Service

1. **Create Web Service**:
   - Name: `fmea-backend`
   - Environment: `Docker`
   - Dockerfile Path: `./Dockerfile.backend`
   - Docker Context: `.`
   - Plan: `Starter`

2. **Set Environment Variables**:
   ```
   ENVIRONMENT=production
   CORS_ORIGINS=https://fmea-frontend.onrender.com
   DATABASE_URL=sqlite:////app/db/fmea.db
   SECRET_KEY=your-secret-key
   OPENAI_API_KEY=your-openai-key
   PORT=8000
   ```

### Frontend Service

1. **Create Web Service**:
   - Name: `fmea-frontend`
   - Environment: `Docker`
   - Dockerfile Path: `./Dockerfile.frontend`
   - Docker Context: `.`
   - Plan: `Starter`

2. **Set Environment Variables**:
   ```
   VITE_API_BASE_URL=https://fmea-backend.onrender.com
   BACKEND_URL=https://fmea-backend.onrender.com
   NODE_ENV=production
   PORT=80
   ```

## 🎯 System Features After Deployment

### ✅ Trial System
- **Admin Users**: Unlimited AI generations
  - `john@fotonconsulting.com`
  - `admin@foton.com`
- **Trial Users**: 5 AI generations per day
  - All other authorized emails
- **Daily Reset**: Limits reset at midnight

### ✅ User Management
- **Email Authentication**: Required for all users
- **Local PC Storage**: Email lists saved to Downloads folder
- **Admin Dashboard**: Monitor all user activity
- **Login Notifications**: Sent to admin on each login

### ✅ Admin Features
- **Usage Dashboard**: Track all user AI generation usage
- **Email Management**: Add/remove authorized users
- **Login Notifications**: View all login activity
- **User Limits**: Reset daily usage for any user

## 🔍 Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check Docker logs in Render dashboard
   - Verify all files are committed to GitHub
   - Ensure Dockerfile paths are correct

2. **Frontend Not Loading**:
   - Check if backend is running
   - Verify `VITE_API_BASE_URL` is correct
   - Check browser console for errors

3. **Backend Errors**:
   - Check environment variables
   - Verify `OPENAI_API_KEY` is set
   - Check database initialization

4. **CORS Issues**:
   - Verify `CORS_ORIGINS` includes frontend URL
   - Check if both services are running

### Debug Commands

```bash
# Check backend health
curl https://fmea-backend.onrender.com/health

# Check backend root
curl https://fmea-backend.onrender.com/

# Check frontend
curl https://fmea-frontend.onrender.com/
```

## 📊 Monitoring

### Render Dashboard
- **Service Status**: Monitor uptime and performance
- **Logs**: View real-time application logs
- **Metrics**: CPU, memory, and response time
- **Environment**: Manage environment variables

### Application Monitoring
- **Usage Dashboard**: Track AI generation usage
- **Login Notifications**: Monitor user activity
- **Trial Status**: View user limits and warnings

## 🚀 Post-Deployment

1. **Test All Features**:
   - Login with different user types
   - Test AI generation limits
   - Verify admin dashboard
   - Check email notifications

2. **Monitor Usage**:
   - Check usage dashboard regularly
   - Monitor trial user activity
   - Review login notifications

3. **User Management**:
   - Add new authorized users
   - Monitor user limits
   - Reset daily usage as needed

## 📞 Support

- **Admin Contact**: john@fotonconsulting.com
- **System Admin**: admin@foton.com
- **Render Support**: [render.com/support](https://render.com/support)

---

**Your FMEA system is now ready for production with complete trial management!** 🎯

