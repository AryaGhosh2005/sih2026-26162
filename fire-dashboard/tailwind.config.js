/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: "#05080f",
        panel: "#0a1019",
        panel2: "#0d131e",
        border: "#1b2635",
        border2: "#283446",
        muted: "#8490a2",
        text: "#e8edf5",
        accent: "#24aef5",
      },
      boxShadow: {
        glow: "0 0 8px var(--tw-shadow-color), 0 0 16px var(--tw-shadow-color)",
      },
    },
  },
  plugins: [],
};
