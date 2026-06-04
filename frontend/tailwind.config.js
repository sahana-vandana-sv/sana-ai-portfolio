/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Soft pastel palette matching the reference
        cream: "#F3E9D2",
        butter: "#F7E7C4",
        lilac: "#D9CFF5",
        lilacSoft: "#E7DEFB",
        mint: "#CFE6DD",
        mintSoft: "#DCEFE7",
        blush: "#F6D6D6",
        sky: "#C9D8F5",
        ink: "#1A1A1A",
        cloud: "#F6F7F8",
        surface: "#FFFFFF",
      },
      fontFamily: {
        sans: ["Poppins", "Inter", "system-ui", "sans-serif"],
      },
      borderRadius: {
        card: "28px",
        tile: "24px",
        pill: "9999px",
      },
      boxShadow: {
        soft: "0 12px 40px -12px rgba(0,0,0,0.12)",
        card: "0 8px 30px -10px rgba(0,0,0,0.10)",
      },
    },
  },
  plugins: [],
};
