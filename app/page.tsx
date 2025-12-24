export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            NWPU AskMe
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            西北工业大学问答平台
          </p>
          <p className="text-lg text-gray-500">
            Northwestern Polytechnical University Q&A Platform
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              欢迎来到 NWPU AskMe
            </h2>
            <p className="text-gray-600 mb-4">
              这是一个专为西北工业大学师生打造的问答交流平台，旨在促进知识分享和学术交流。
            </p>
            <div className="grid md:grid-cols-3 gap-6 mt-8">
              <div className="text-center p-6 bg-blue-50 rounded-lg">
                <div className="text-4xl mb-2">💬</div>
                <h3 className="font-semibold text-gray-800 mb-2">提问交流</h3>
                <p className="text-sm text-gray-600">
                  在这里提出你的问题，获得社区的帮助
                </p>
              </div>
              <div className="text-center p-6 bg-green-50 rounded-lg">
                <div className="text-4xl mb-2">📚</div>
                <h3 className="font-semibold text-gray-800 mb-2">知识分享</h3>
                <p className="text-sm text-gray-600">
                  分享你的知识和经验，帮助他人成长
                </p>
              </div>
              <div className="text-center p-6 bg-purple-50 rounded-lg">
                <div className="text-4xl mb-2">🤝</div>
                <h3 className="font-semibold text-gray-800 mb-2">学术交流</h3>
                <p className="text-sm text-gray-600">
                  与同学和老师进行深入的学术讨论
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Quick Start
            </h2>
            <ul className="space-y-3 text-gray-600">
              <li className="flex items-start">
                <span className="text-blue-500 font-bold mr-2">1.</span>
                <span>Browse questions and answers from the community</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-500 font-bold mr-2">2.</span>
                <span>Ask your own questions and get help from others</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-500 font-bold mr-2">3.</span>
                <span>Share your knowledge by answering questions</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-500 font-bold mr-2">4.</span>
                <span>Connect with fellow students and faculty members</span>
              </li>
            </ul>
          </div>
        </div>

        <footer className="text-center mt-16 text-gray-500">
          <p>© 2024 NWPU AskMe - Powered by Vercel</p>
        </footer>
      </div>
    </main>
  )
}
