import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer id="footer" className="bg-gray-800 text-gray-300 py-10 px-6 mt-10">
      <div className="container mx-auto max-w-6xl">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-white font-bold text-lg mb-4">Foton aiFMEA Builder</h3>
            <p className="text-gray-400 text-sm">The most advanced AI-powered FMEA solution for engineering teams and quality professionals.</p>
          </div>
          <div>
            <h4 className="text-white font-medium mb-4">Product</h4>
            <ul className="space-y-2">
              <li><span className="text-gray-400 hover:text-white text-sm cursor-pointer">Features</span></li>
              <li><span className="text-gray-400 hover:text-white text-sm cursor-pointer">Pricing</span></li>
              <li><span className="text-gray-400 hover:text-white text-sm cursor-pointer">Case Studies</span></li>
              <li><span className="text-gray-400 hover:text-white text-sm cursor-pointer">Testimonials</span></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-medium mb-4">Resources</h4>
            <ul className="space-y-2">
              <li><span className="text-gray-400 hover:text-white text-sm cursor-pointer">Documentation</span></li>
              <li><span className="text-gray-400 hover:text-white text-sm cursor-pointer">Knowledge Base</span></li>
              <li><span className="text-gray-400 hover:text-white text-sm cursor-pointer">API</span></li>
              <li><span className="text-gray-400 hover:text-white text-sm cursor-pointer">Community</span></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-medium mb-4">Company</h4>
            <ul className="space-y-2">
              <li><span className="text-gray-400 hover:text-white text-sm cursor-pointer">About</span></li>
              <li><span className="text-gray-400 hover:text-white text-sm cursor-pointer">Privacy</span></li>
              <li><span className="text-gray-400 hover:text-white text-sm cursor-pointer">Terms</span></li>
              <li><span className="text-gray-400 hover:text-white text-sm cursor-pointer">Contact Support</span></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-700 mt-8 pt-6 flex justify-between items-center">
          <div className="text-gray-500 text-sm">© 2023 Foton aiFMEA Builder. All rights reserved.</div>
          <div className="flex space-x-4">
            <span className="text-gray-400 hover:text-white cursor-pointer"><i className="fa-brands fa-twitter"></i></span>
            <span className="text-gray-400 hover:text-white cursor-pointer"><i className="fa-brands fa-linkedin"></i></span>
            <span className="text-gray-400 hover:text-white cursor-pointer"><i className="fa-brands fa-github"></i></span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 