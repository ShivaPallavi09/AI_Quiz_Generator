import React from 'react';

// This is a reusable component to display the full quiz data
export default function QuizDisplay({ quizData }) {
  if (!quizData) return null;

  const { title, summary, key_entities, quiz, related_topics } = quizData;

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-800">{title}</h2>
      
      {/* --- Summary --- */}
      <Section title="Summary">
        <p className="text-gray-700">{summary}</p>
      </Section>

      {/* --- Key Entities --- */}
      <Section title="Key Entities">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <EntityList title="People" items={key_entities.people} />
          <EntityList title="Organizations" items={key_entities.organizations} />
          <EntityList title="Locations" items={key_entities.locations} />
        </div>
      </Section>

      {/* --- Quiz Questions --- */}
      <Section title="Generated Quiz">
        <div className="space-y-4">
          {quiz.map((q, index) => (
            <div key={index} className="p-4 border border-gray-200 rounded-lg bg-gray-50">
              <p className="font-semibold text-gray-800">
                {index + 1}. {q.question}
              </p>
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                q.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                q.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {q.difficulty}
              </span>
              <div className="mt-2 space-y-1">
                {q.options.map((option, i) => (
                  <p key={i} className={`
                    block p-2 rounded
                    ${option === q.answer ? 'bg-green-100 font-medium text-green-900' : 'text-gray-700'}
                  `}>
                    {option}
                  </p>
                ))}
              </div>
              <p className="mt-2 text-sm text-gray-600 italic">
                <strong>Explanation:</strong> {q.explanation}
              </p>
            </div>
          ))}
        </div>
      </Section>

      {/* --- Related Topics --- */}
      <Section title="Related Topics">
        <div className="flex flex-wrap gap-2">
          {related_topics.map((topic, index) => (
            <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
              {topic}
            </span>
          ))}
        </div>
      </Section>
    </div>
  );
}

// Helper sub-components
const Section = ({ title, children }) => (
  <div className="border-b border-gray-200 pb-4">
    <h3 className="text-xl font-semibold text-gray-700 mb-3">{title}</h3>
    {children}
  </div>
);

const EntityList = ({ title, items }) => (
  <div>
    <h4 className="font-semibold text-gray-600">{title}</h4>
    <ul className="list-disc list-inside text-gray-600 text-sm">
      {items.map((item, i) => <li key={i}>{item}</li>)}
    </ul>
  </div>
);