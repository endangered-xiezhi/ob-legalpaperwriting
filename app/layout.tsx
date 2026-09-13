import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("http://localhost:3000"),
  title: "LexTrace｜Obsidian 法学研究工作台",
  description: "连接本地 Obsidian 知识产权库，完成知网采集、待处理筛选、关系分析、法学引注与研究包导出。",
  openGraph: {
    title: "LexTrace｜Obsidian 法学研究工作台",
    description: "从知网采集到法学引注，所有研究材料始终回到本地 Obsidian。",
    images: [{ url: "/og.png", width: 1200, height: 630, alt: "LexTrace Obsidian 法学研究导览" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "LexTrace｜Obsidian 法学研究工作台",
    description: "从知网采集到法学引注，所有研究材料始终回到本地 Obsidian。",
    images: ["/og.png"],
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
