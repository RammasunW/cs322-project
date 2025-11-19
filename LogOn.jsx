import { useState } from 'react';
import { Eye, EyeOff, User, Mail, Lock, Key, ArrowLeft, CheckCircle, Utensils } from 'lucide-react';

// --- Utility Components ---

// 1. ImageWithFallback Component (Handles background image and error fallback)
const ImageWithFallback = ({ src, alt, className }) => {
  const [imageSrc, setImageSrc] = useState(src);
  const [hasError, setHasError] = useState(false);
  
  const fallbackSrc = "https://placehold.co/1920x1080/1e293b/ffffff?text=W+Restaurant+Background";

  const handleError = () => {
    if (!hasError) {
      setImageSrc(fallbackSrc);
      setHasError(true);
    }
  };

  return (
    <img
      src={imageSrc}
      alt={alt}
      className={className}
      onError={handleError}
    />
  );
};

// 2. Common Input Field Component
const InputField = ({ label, id, type, placeholder, value, onChange, icon: Icon, isPasswordToggle = false, showPassword, setShowPassword }) => (
  <div>
    <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-2">
      {label}
    </label>
    <div className="relative">
      {Icon && (
        <Icon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
      )}
      <input
        id={id}
        type={type}
        value={value}
        // IMPORTANT: The onChange handler is passed directly and correctly updates state
        onChange={onChange}
        className={`w-full px-4 py-3 ${Icon ? 'pl-12' : ''} ${isPasswordToggle ? 'pr-12' : ''} border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-all shadow-sm bg-gray-50`}
        placeholder={placeholder}
        required
      />
      {isPasswordToggle && (
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-red-600 transition-colors"
          aria-label={showPassword ? 'Hide password' : 'Show password'}
        >
          {showPassword ? (
            <EyeOff className="w-5 h-5" />
          ) : (
            <Eye className="w-5 h-5" />
          )}
        </button>
      )}
    </div>
  </div>
);

// --- View Components (Defined outside App for stability and to fix the focus issue) ---

const AuthView = ({ state, handlers }) => {
    const { mode, showPassword, loginEmail, loginPassword, registerName, registerEmail, registerPassword, employeeIdOrEmail } = state;
    const { setMode, handleLogin, handleRegister, setView, setLoginEmail, setLoginPassword, setRegisterName, setRegisterEmail, setRegisterPassword, setEmployeeIdOrEmail, setShowPassword } = handlers;
    
    return (
        <>
            {/* Tabs (Only visible for customer login/register) */}
            <div className={`flex gap-4 mb-8 border-b border-gray-200 ${mode === 'employeeLogin' ? 'hidden' : ''}`}>
                <button
                    onClick={() => setMode('customerLogin')}
                    className={`pb-3 relative transition-colors font-semibold ${
                        mode === 'customerLogin' ? 'text-red-600' : 'text-gray-500 hover:text-gray-700'
                    }`}
                >
                    Customer Log In
                    {mode === 'customerLogin' && (
                        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-red-600 transition-all" />
                    )}
                </button>
                <button
                    onClick={() => setMode('customerRegister')}
                    className={`pb-3 relative transition-colors font-semibold ${
                        mode === 'customerRegister' ? 'text-red-600' : 'text-gray-500 hover:text-gray-700'
                    }`}
                >
                    Register
                    {mode === 'customerRegister' && (
                        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-red-600 transition-all" />
                    )}
                </button>
            </div>

            {/* Employee Back Button */}
            {mode === 'employeeLogin' && (
                <button 
                    onClick={() => setMode('customerLogin')} 
                    className="flex items-center text-sm font-medium text-gray-500 hover:text-red-600 mb-6 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4 mr-2"/> Back to Customer Login
                </button>
            )}

            {/* Customer Login Form */}
            {mode === 'customerLogin' && (
                <form onSubmit={handleLogin} className="space-y-6">
                    <InputField
                        label="Email Address"
                        id="login-email"
                        type="email"
                        placeholder="user@example.com"
                        value={loginEmail}
                        onChange={(e) => setLoginEmail(e.target.value)}
                        icon={Mail}
                    />
                    <InputField
                        label="Password"
                        id="login-password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="Enter your password"
                        value={loginPassword}
                        onChange={(e) => setLoginPassword(e.target.value)}
                        icon={Lock}
                        isPasswordToggle={true}
                        showPassword={showPassword}
                        setShowPassword={setShowPassword}
                    />
                    <button
                        type="submit"
                        className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 rounded-xl transition-all shadow-md focus:outline-none focus:ring-4 focus:ring-red-300 transform hover:scale-[1.005]"
                    >
                        Log In
                    </button>
                    <div className="flex justify-between pt-2">
                        <button 
                            type="button" 
                            onClick={() => setView('forgotPassword')} 
                            className="text-sm text-gray-500 hover:text-red-600 hover:underline transition-colors"
                        >
                            Forgot Password?
                        </button>
                        <button 
                            type="button" 
                            onClick={() => setMode('employeeLogin')} 
                            className="text-sm text-gray-500 hover:text-red-600 hover:underline transition-colors"
                        >
                            Employee Login
                        </button>
                    </div>
                </form>
            )}

            {/* Customer Register Form */}
            {mode === 'customerRegister' && (
                <form onSubmit={handleRegister} className="space-y-6">
                    <InputField
                        label="Full Name"
                        id="register-name"
                        type="text"
                        placeholder="Your full name"
                        value={registerName}
                        onChange={(e) => setRegisterName(e.target.value)}
                        icon={User}
                    />
                    <InputField
                        label="Email Address"
                        id="register-email"
                        type="email"
                        placeholder="user@example.com"
                        value={registerEmail}
                        onChange={(e) => setRegisterEmail(e.target.value)}
                        icon={Mail}
                    />
                    <InputField
                        label="Password"
                        id="register-password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="Create a password"
                        value={registerPassword}
                        onChange={(e) => setRegisterPassword(e.target.value)}
                        icon={Lock}
                        isPasswordToggle={true}
                        showPassword={showPassword}
                        setShowPassword={setShowPassword}
                    />
                    <button
                        type="submit"
                        className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 rounded-xl transition-all shadow-md focus:outline-none focus:ring-4 focus:ring-red-300 transform hover:scale-[1.005]"
                    >
                        Create Account
                    </button>
                </form>
            )}

            {/* Employee Login Form */}
            {mode === 'employeeLogin' && (
                <form onSubmit={handleLogin} className="space-y-6">
                    <InputField
                        label="Employee ID or Email"
                        id="employee-id-email"
                        type="text"
                        placeholder="Your ID or work email"
                        value={employeeIdOrEmail}
                        onChange={(e) => setEmployeeIdOrEmail(e.target.value)}
                        icon={Key}
                    />
                    <InputField
                        label="Password"
                        id="employee-password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="Enter your password"
                        value={loginPassword}
                        onChange={(e) => setLoginPassword(e.target.value)}
                        icon={Lock}
                        isPasswordToggle={true}
                        showPassword={showPassword}
                        setShowPassword={setShowPassword}
                    />
                    <button
                        type="submit"
                        className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 rounded-xl transition-all shadow-md focus:outline-none focus:ring-4 focus:ring-red-300 transform hover:scale-[1.005]"
                    >
                        Employee Log In
                    </button>
                </form>
            )}
        </>
    );
};

const ForgotPasswordView = ({ handlers, state }) => {
    const { setView, handleForgotPasswordSubmit } = handlers;
    const { forgotPasswordEmail } = state;
    const { setForgotPasswordEmail } = handlers;

    return (
        <div className="space-y-6">
            <button 
                onClick={() => setView('auth')} 
                className="flex items-center text-sm font-medium text-gray-500 hover:text-red-600 mb-6 transition-colors"
            >
                <ArrowLeft className="w-4 h-4 mr-2"/> Back to Log In
            </button>

            <p className="text-gray-500 text-center mb-6">
                Enter your email address and we will send you a link to reset your password.
            </p>

            <form onSubmit={handleForgotPasswordSubmit} className="space-y-6">
                <InputField
                    label="Email Address"
                    id="forgot-email"
                    type="email"
                    placeholder="user@example.com"
                    value={forgotPasswordEmail}
                    onChange={(e) => setForgotPasswordEmail(e.target.value)}
                    icon={Mail}
                />
                <button
                    type="submit"
                    className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 rounded-xl transition-all shadow-md focus:outline-none focus:ring-4 focus:ring-red-300 transform hover:scale-[1.005]"
                >
                    Send Reset Link
                </button>
            </form>
        </div>
    );
};

const SuccessView = ({ handlers, state }) => {
    const { resetView } = handlers;
    const { successMessage } = state;

    return (
        <div className="text-center p-8">
            <CheckCircle className="w-16 h-16 mx-auto text-green-500 mb-4 animate-bounce" />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Success!</h2>
            <p className="text-gray-600 mb-6">{successMessage}</p>
            <button
                onClick={resetView}
                className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 rounded-xl transition-colors focus:outline-none"
            >
                Continue
            </button>
        </div>
    );
};


// --- Main Application Component ---

export default function App() {
  // State for UI management: 'auth' (default), 'forgotPassword', 'success'
  const [view, setView] = useState('auth'); 
  // State for form mode: 'customerLogin', 'customerRegister', 'employeeLogin'
  const [mode, setMode] = useState('customerLogin'); 
  const [showPassword, setShowPassword] = useState(false);
  const [successMessage, setSuccessMessage] = useState(null); 

  // Customer/Employee Form Data States
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [registerName, setRegisterName] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [employeeIdOrEmail, setEmployeeIdOrEmail] = useState('');
  const [forgotPasswordEmail, setForgotPasswordEmail] = useState('');

  // --- Handlers ---

  const handleLogin = (e) => {
    e.preventDefault();
    const userType = mode === 'employeeLogin' ? 'Employee' : 'Customer';
    setSuccessMessage(`${userType} login successful! Welcome to W Restaurant.`);
    setView('success');
  };

  const handleRegister = (e) => {
    e.preventDefault();
    setSuccessMessage(`Registration successful for ${registerName}! You can now log in.`);
    setView('success');
  };

  const handleForgotPasswordSubmit = (e) => {
    e.preventDefault();
    setSuccessMessage(`Password reset link successfully sent to ${forgotPasswordEmail}.`);
    setView('success');
  };
  
  const resetView = () => {
    setView('auth');
    setSuccessMessage(null);
    setMode('customerLogin');
  };

  // --- Logic for Subtitle Text ---
  const getSubtitle = () => {
    if (view === 'forgotPassword') return "Reset your password";
    if (mode === 'customerLogin') return "Returning Customer?";
    if (mode === 'customerRegister') return "Become a Member";
    if (mode === 'employeeLogin') return "Staff Access Only";
    return "";
  };
  
  // Aggregate state and handlers to pass as props
  const sharedState = {
    mode, view, successMessage, showPassword,
    loginEmail, loginPassword, registerName, registerEmail, registerPassword, employeeIdOrEmail, forgotPasswordEmail
  };

  const sharedHandlers = {
    setMode, setView, setShowPassword, handleLogin, handleRegister, handleForgotPasswordSubmit, resetView,
    setLoginEmail, setLoginPassword, setRegisterName, setRegisterEmail, setRegisterPassword, setEmployeeIdOrEmail, setForgotPasswordEmail
  };


  // --- Main Render ---
  return (
    <div className="relative w-screen h-screen overflow-hidden font-inter">
      {/* Background Image with Blur, Darken, and Vignette */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src="https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1920&q=80"
          alt="Gourmet dish background"
          className="w-full h-full object-cover"
        />
        {/* Blur, Darken and Vignette Overlay (Responsive and slightly less blur) */}
        <div 
          className="absolute inset-0 backdrop-blur-sm bg-black/50"
          style={{
            boxShadow: 'inset 0 0 300px 100px rgba(0, 0, 0, 0.4)'
          }}
        />
      </div>

      {/* Centered Form Box (Responsive Layout) */}
      <div className="relative flex items-center justify-center w-full h-full p-4 sm:p-8">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 sm:p-10 transition-all duration-300">
          
          {/* Header */}
          <div className="text-center mb-8">
            {view !== 'success' && (
                <Utensils className="w-8 h-8 text-red-600 mx-auto mb-2" />
            )}
            {view !== 'success' && (
                <>
                    <h1 className="text-3xl font-bold text-gray-900 mb-1">
                      W Restaurant
                    </h1>
                    <p className="text-gray-500 font-medium">
                      {getSubtitle()}
                    </p>
                </>
            )}
          </div>

          {/* Conditional View Rendering */}
          {view === 'auth' && <AuthView state={sharedState} handlers={sharedHandlers} />}
          {view === 'forgotPassword' && <ForgotPasswordView state={sharedState} handlers={sharedHandlers} />}
          {view === 'success' && <SuccessView state={sharedState} handlers={sharedHandlers} />}

        </div>
      </div>
    </div>
  );
}