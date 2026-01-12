export function isProbablyHtml(s?: string) {
  const v = (s || '').trim();
  if (!v) return false;
  return v.startsWith('<') || v.includes('<html') || v.includes('<table') || v.includes('<body');
}

export function htmlToText(html: string) {
  try {
    const doc = new DOMParser().parseFromString(html, 'text/html');
    const text = (doc.body?.textContent || '').replace(/\n\s+\n/g, '\n\n').trim();
    return text || '(No text content)';
  } catch {
    return '(Unable to parse HTML)';
  }
}

