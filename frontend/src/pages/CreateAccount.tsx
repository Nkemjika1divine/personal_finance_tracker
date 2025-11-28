import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";

export default function CreateAccount() {
  const [username, setUsername] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  const handleCreateAccount = (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);

    // Simulate API call
    setTimeout(() => {
      setLoading(false);
      alert("Account creation successful!");
    }, 1500);
  };

  const handleSocialLogin = (provider: string) => {
    alert(`Logging in with ${provider}`)
  }

  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-200 px-4">
      <div className="bg-white shadow-2xl rounded-3xl max-w-md w-full p-10 relative overflow-hidden">
        {/* Red Header */}
        <div className="absolute -top-20 -left-20 w-72 h-72 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>

        <h1 className="text-3xl font-bold text-center text-black mb-6 z-10 relative">
          Hello, Welcome
        </h1>
        <p className="text-center text-black mb-8 z-10 relative">
          Create your account
        </p>

        <form onSubmit={handleCreateAccount} className="space-y-6 z-10 relative">
          {/* Username */}
          <div className="relative">
            <input
              type="username"
              id="username"
              placeholder=" "
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="peer w-full border border-gray-300 rounded-xl px-4 pt-5 pb-2 text-sm text-black focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
              required
            />
            <label
              htmlFor="username"
              className="absolute left-4 top-2 text-gray-500 text-sm transition-all peer-placeholder-shown:top-5 peer-placeholder-shown:text-gray-500 peer-placeholder-shown:text-base peer-focus:top-2 peer-focus:textblue-600 peer-focus:text-sm"
            >
              Username
            </label>
          </div>

          {/* Email */}
          <div className="relative">
            <input
              type="email"
              id="email"
              placeholder=" "
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="peer w-full border border-gray-300 rounded-xl px-4 pt-5 pb-2 text-sm text-black focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
              required
            />
            <label
              htmlFor="email"
              className="absolute left-4 top-2 text-gray-500 text-sm transition-all peer-placeholder-shown:top-5 peer-placeholder-shown:text-gray-500 peer-placeholder-shown:text-base peer-focus:top-2 peer-focus:textblue-600 peer-focus:text-sm"
            >
              Email
            </label>
          </div>

          {/* Password */}
          <div className="relative">
            <input
              type="password"
              id="password"
              placeholder=" "
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="peer w-full border border-gray-300 rounded-xl px-4 pt-5 pb-2 text-sm text-black focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
              required
            />
            <label
              htmlFor="password"
              className="absolute left-4 top-2 text-gray-500 text-sm transition-all peer-placeholder-shown:top-5 peer-placeholder-shown:text-gray-500 peer-placeholder-shown:text-base peer-focus:top-2 peer-focus:textblue-600 peer-focus:text-sm"
            >
              Password
            </label>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-red-600 text-white py-3 rounded-xl text-lg font-semibold hover:bg-red-700 transition flex justify-center items-center"
          >
            {loading ? (
              <svg
                className="animate-spin h-5 w-5 mr-2 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8v8H4z"
                ></path>
              </svg>
            ) : null}
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        {/* Or divider */}
        <div className="flex items-center my-6 relative z-10">
          <hr className="flex-1 border-gray-300" />
          <span className="mx-4 text-gray-500 text-sm">or continue with</span>
          <hr className="flex-1 border-gray-300" />
        </div>

        {/* Social Auth Buttons */}
        <div className="flex flex-col gap-4 relative z-10">
          <button
            onClick={() => handleSocialLogin("Google")}
            className="flex items-center justify-center gap-2 w-full border border-gray-300 rounded-xl py-2 text-black hover:bg-gray-100 transition"
          >
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" alt="Google" className="w-5 h-5" />
            Continue with Google
          </button>

          <button
            onClick={() => handleSocialLogin("Apple")}
            className="flex items-center justify-center gap-2 w-full border border-gray-300 rounded-xl py-2 text-black hover:bg-gray-100 transition"
          >
            <img src="https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg" alt="Apple" className="w-5 h-5" />
            Continue with Apple
          </button>

          <button
            onClick={() => handleSocialLogin("Microsoft")}
            className="flex items-center justify-center gap-2 w-full border border-gray-300 rounded-xl py-2 text-black hover:bg-gray-100 transition"
          >
            <img src="https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg" alt="Microsoft" className="w-5 h-5" />
            Continue with Microsoft
          </button>
        </div>

        {/* Already have an account section*/}
        <div className="mt-6 text-center relative z-10">
          <p className="text-gray-600 text-sm">
            Already have an account?{" "}
            <span className="text-blue-600 font-semibold cursor-pointer hover:underline" onClick={() => navigate("/login")}>
              Login
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}
