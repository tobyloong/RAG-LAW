import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { CopyToClipboard } from 'react-copy-to-clipboard';

const MarkdownRenderer = ({ content, citations = [], onCitationClick }) => {
  const [copiedStates, setCopiedStates] = useState({});

  const handleCopy = (code) => {
    const newState = { ...copiedStates };
    newState[code] = true;
    setCopiedStates(newState);
    
    setTimeout(() => {
      const resetState = { ...copiedStates };
      resetState[code] = false;
      setCopiedStates(resetState);
    }, 3000);
  };

  // 处理<think>标签
  const processThinkTags = (text) => {
    const parts = text.split(/<\/?think>/g);
    return parts.map((part, index) => {
      if (index % 2 === 1) { // 这是<think>标签内的内容
        return `\n\n> 💭 思考过程：\n> ${part.split('\n').join('\n> ')}\n\n`;
      }
      return part;
    }).join('');
  };

  // 处理[citation:X]标签
  const processCitations = (text) => {
    // 使用正则表达式匹配所有引用标签
    const citationRegex = /\[citation:(\d+)\]/g;
    let lastIndex = 0;
    const parts = [];
    let match;

    while ((match = citationRegex.exec(text)) !== null) {
      // 添加引用标签之前的文本
      parts.push(text.slice(lastIndex, match.index));
      
      const citationIndex = parseInt(match[1]);
      // 获取引用内容来判断类型
      const citation = citations[citationIndex - 1] || '';
      let citationType = '案例';
      if (citation.startsWith('[法条')) {
        citationType = '法条';
      } else if (citation.startsWith('[问答')) {
        citationType = '问答';
      }
      
      // 添加特殊的markdown标记
      parts.push(`[${citationType}${match[1]}](#citation-${match[1]})`);
      
      lastIndex = match.index + match[0].length;
    }
    
    // 添加剩余的文本
    parts.push(text.slice(lastIndex));
    
    return parts.join('');
  };

  // 处理文本内容
  const processContent = (text) => {
    const withThinkTags = processThinkTags(text);
    return processCitations(withThinkTags);
  };

  const processedContent = processContent(content);

  return (
    <div className="relative z-0">
      <ReactMarkdown
        remarkPlugins={[remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const code = String(children).replace(/\n$/, '');

            return !inline && match ? (
              <div className="relative group z-0">
                <SyntaxHighlighter
                  style={tomorrow}
                  language={match[1]}
                  PreTag="div"
                  className="rounded-lg"
                  {...props}
                >
                  {code}
                </SyntaxHighlighter>
                <CopyToClipboard text={code} onCopy={() => handleCopy(code)}>
                  <button
                    className="absolute top-2 right-2 bg-gray-700 text-white px-2 py-1 rounded text-sm opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    {copiedStates[code] ? '已复制!' : '复制'}
                  </button>
                </CopyToClipboard>
              </div>
            ) : (
              <code className={`${className} bg-gray-100 rounded-md px-1`} {...props}>
                {children}
              </code>
            );
          },
          a({ node, children, href, ...props }) {
            if (href?.startsWith('#citation-')) {
              const id = parseInt(href.replace('#citation-', ''));
              return (
                <button
                  onClick={() => onCitationClick(id)}
                  className="inline-flex items-center px-2 py-1 mx-1 text-xs font-medium text-gray-600 bg-gray-100 rounded hover:bg-gray-200 transition-colors z-0"
                >
                  {children}
                </button>
              );
            }
            return (
              <a 
                className="text-blue-500 hover:text-blue-700 underline z-0" 
                target="_blank"
                rel="noopener noreferrer"
                href={href}
                {...props}
              >
                {children}
              </a>
            );
          },
          h1: ({ children, ...props }) => (
            <h1 className="text-2xl font-bold my-4" {...props}>
              {children}
            </h1>
          ),
          h2: ({ children, ...props }) => (
            <h2 className="text-xl font-bold my-3" {...props}>
              {children}
            </h2>
          ),
          h3: ({ children, ...props }) => (
            <h3 className="text-lg font-bold my-2" {...props}>
              {children}
            </h3>
          ),
          p: ({ children, ...props }) => (
            <p className="my-2" {...props}>
              {children}
            </p>
          ),
          ul: ({ children, ...props }) => (
            <ul className="list-disc list-inside my-2" {...props}>
              {children}
            </ul>
          ),
          ol: ({ children, ...props }) => (
            <ol className="list-decimal list-inside my-2" {...props}>
              {children}
            </ol>
          ),
          blockquote: ({ children, ...props }) => (
            <blockquote className="border-l-4 border-gray-300 pl-4 my-4 py-2 bg-gray-50 rounded-r" {...props}>
              {children}
            </blockquote>
          ),
        }}
      >
        {processedContent}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer; 