import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export default function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  return (
    <ReactMarkdown
      className={`prose prose-sm max-w-none text-foreground ${className}`}
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeRaw]}
      components={{
        h1: ({ node, ...props }) => <h1 className="text-2xl font-bold mt-6 mb-4" {...props} />,
        h2: ({ node, ...props }) => <h2 className="text-xl font-bold mt-5 mb-3" {...props} />,
        h3: ({ node, ...props }) => <h3 className="text-lg font-semibold mt-4 mb-2" {...props} />,
        p: ({ node, ...props }) => <p className="mb-3 leading-relaxed" {...props} />,
        ul: ({ node, ...props }) => <ul className="list-disc pl-6 mb-3 space-y-1" {...props} />,
        ol: ({ node, ...props }) => <ol className="list-decimal pl-6 mb-3 space-y-1" {...props} />,
        li: ({ node, ...props }) => <li className="leading-relaxed" {...props} />,
        blockquote: ({ node, ...props }) => (
          <blockquote className="border-l-4 border-primary pl-4 italic my-4 text-muted-foreground" {...props} />
        ),
        code: ({ inline, ...props }: any) =>
          inline ? (
            <code className="bg-secondary px-1.5 py-0.5 rounded text-sm font-mono" {...props} />
          ) : (
            <code className="block bg-secondary p-4 rounded-lg overflow-x-auto font-mono text-sm my-3" {...props} />
          ),
        a: ({ node, ...props }) => (
          <a className="text-primary hover:underline" target="_blank" rel="noopener noreferrer" {...props} />
        ),
        strong: ({ node, ...props }) => <strong className="font-bold" {...props} />,
        em: ({ node, ...props }) => <em className="italic" {...props} />,
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
