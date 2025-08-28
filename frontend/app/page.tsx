import Link from 'next/link';
export default function Page() {
  return (<main className="space-y-6">
    <h1 className="text-2xl font-semibold">DanceApp — Home</h1>
    <ul className="list-disc ml-6">
      <li><Link className="underline" href="/upload">Upload & Analyze</Link></li>
      <li><Link className="underline" href="/moves">Move Library</Link></li>
      <li><Link className="underline" href="/composer">Composer</Link></li>
    </ul>
  </main>);
}