import React, { useState } from 'react';
import GenerateQuizTab from './tabs/GenerateQuizTab';
import HistoryTab from './tabs/HistoryTab';

function App() {
  const [activeTab, setActiveTab] = useState('generate');

  const TabButton = ({ tabName, title }) => (
    <button
      onClick={() => setActiveTab(tabName)}
      className={`px-6 py-3 text-lg font-medium rounded-t-lg
        ${activeTab === tabName 
          ? 'text-blue-600 border-b-2 border-blue-600' 
          : 'text-gray-500 hover:text-gray-700'
        }
      `}
    >
      {title}
    </button>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto p-4 md:p-8">
        
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-4xl font-extrabold text-gray-800">
            AI Wiki Quiz Generator
          </h1>
          <p className="text-lg text-gray-600 mt-2">
            Powered by FastAPI, React, and Gemini
          </p>
        </header>
        
        {/* Tab Navigation */}
        <div className="mb-6 border-b border-gray-200">
          <nav className="flex -mb-px">
            <TabButton tabName="generate" title="Generate Quiz" />
            <TabButton tabName="history" title="Past Quizzes (History)" />
          </nav>
        </div>

        {/* Tab Content */}
        <main>
          {activeTab === 'generate' && <GenerateQuizTab />}
          {activeTab === 'history' && <HistoryTab />}
        </main>
      </div>
    </div>
  );
}

export default App;
