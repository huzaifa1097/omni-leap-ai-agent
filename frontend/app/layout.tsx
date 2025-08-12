import type { Metadata } from "next";
// Import the 'Sora' font from Google Fonts
import { Sora } from "next/font/google";
import "./globals.css";

// Configure the font
const sora = Sora({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "OmniLeap Agent",
  description: "The Unified Intelligence Agent",
  icons: {
    icon: "/omni-leap-logo.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      {/* Apply the font class to the body */}
      <body className={`${sora.className} bg-gray-900 text-white`}>
        {children}
      </body>
    </html>
  );
}
