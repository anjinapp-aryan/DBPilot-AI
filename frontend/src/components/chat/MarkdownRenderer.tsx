import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { SqlCodeBlock } from "./SqlCodeBlock";

export function MarkdownRenderer({ content }: { content: string }) {
  return (
    <div className="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-pre:bg-transparent prose-pre:p-0">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code(props) {
            const { className, children, ...rest } = props;
            const match = /language-(\w+)/.exec(className ?? "");
            const isBlock = Boolean(match);
            if (!isBlock) {
              return (
                <code className="rounded bg-surface-2 px-1.5 py-0.5 text-[0.85em]" {...rest}>
                  {children}
                </code>
              );
            }
            return <SqlCodeBlock code={String(children).replace(/\n$/, "")} language={match![1]} />;
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
