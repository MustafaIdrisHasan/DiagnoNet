# DiagnoNet - Medical Diagnosis Interface

A modern, responsive medical diagnosis platform with AI-assisted analysis featuring three specialized agents: Vital Agent, Symptom Agent, and X-ray Agent.

## 🏥 Features

- **Landing Page**: Bold, impactful design with medical tech visualizations
- **Patient Form**: Comprehensive patient information collection with dynamic agent selection
- **Results Page**: Professional diagnosis results display with AI supervisor analysis
- **Responsive Design**: Works seamlessly across all device sizes
- **Medical Visualizations**: DNA helixes, medical icons, and animated elements

## 🎨 Design

- **Typography**: Helvetica font family for bold, impactful design
- **Color Themes**: 
  - Primary: #E61A4F (red), #FB6E92 (pink), #FFFFFF (white)
  - Secondary: #800080 (purple) and white
- **Animations**: Smooth transitions, pulse effects, and floating particles

## 🛠 Tech Stack

- **React.js** - Frontend framework
- **React Router** - Client-side routing
- **Vanilla CSS** - Styling (no external frameworks)
- **Modern ES6+** - JavaScript features

## 📁 Project Structure

```
diagnonet-app/
├── public/
│   └── index.html
├── src/
│   ├── pages/                    # Individual page components
│   │   ├── LandingPage.js       # Home page with DiagnoNet branding
│   │   ├── PatientFormPage.js   # Patient info & agent selection
│   │   └── SupervisorResultsPage.js # Diagnosis results display
│   ├── styles/                   # CSS files for styling
│   │   ├── App.css              # Global styles and variables
│   │   ├── LandingPage.css      # Landing page specific styles
│   │   ├── PatientForm.css      # Form page specific styles
│   │   └── SupervisorResults.css # Results page specific styles
│   ├── App.js                   # Main app component with routing
│   └── index.js                 # React app entry point
├── package.json
└── README.md
```

## 🚀 Getting Started

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm start
   ```

3. **Open Browser**
   Navigate to `http://localhost:3000`

## 📱 Pages

### 1. Landing Page (`/`)
- DIAGONET title with tagline "AI Assist, Not Replace"
- Feature cards for each agent
- Medical tech visualizations
- Call-to-action button to start diagnosis

### 2. Patient Form Page (`/patient-form`)
- General patient information (name, age, condition)
- Agent selection (Vital, Symptom, X-ray)
- Dynamic input fields based on selected agents
- Form validation and submission

### 3. Results Page (`/results`)
- Patient summary with confidence score
- AI supervisor analysis
- Agent contributions breakdown
- Medical recommendations
- Print and new analysis options

## 🔧 Customization

### Adding New Agents
1. Update the agent selection in `PatientFormPage.js`
2. Add corresponding input fields
3. Update the results display in `SupervisorResultsPage.js`

### Styling Changes
- Global styles: `src/styles/App.css`
- Page-specific styles: Individual CSS files in `src/styles/`
- Color themes: CSS variables in `App.css`

### Backend Integration
The frontend is ready for backend integration:
- Form data structure is prepared for API calls
- Loading states are implemented
- Results display accepts dynamic data

## 🎯 Key Components

- **Routing**: React Router for navigation between pages
- **State Management**: React hooks for form data and results
- **Responsive Design**: CSS Grid and Flexbox for layouts
- **Animations**: CSS keyframes for medical visualizations
- **Form Handling**: Controlled components with validation

## 📋 Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

## 🔮 Future Enhancements

- Backend API integration
- Real-time agent processing
- User authentication
- Medical history tracking
- Advanced visualizations
- Multi-language support

## 📄 License

This project is created for medical diagnosis interface demonstration purposes.

---

**Note**: This AI analysis interface is for demonstration purposes only and should not replace professional medical advice. Always consult with qualified healthcare providers for medical diagnosis and treatment.
