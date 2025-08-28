export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (<html lang="en"><head/><body className="p-6">{children}</body></html>);
}