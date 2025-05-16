import React from 'react';
import { BookOpen, ArrowRight } from 'lucide-react';
import Button from '../ui/Button';

const CTA: React.FC = () => {
  return (
    <section className="py-16 bg-blue-600 text-white relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 z-0 opacity-10">
        <div className="absolute top-0 left-0 w-64 h-64 rounded-full bg-white"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 rounded-full bg-white"></div>
      </div>
      
      <div className="container mx-auto px-4 md:px-6 lg:px-8 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">Begin Your Journey to Judaism Today</h2>
          <p className="text-lg md:text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Take the first step toward embracing Jewish traditions, community, and spirituality. Our team is ready to guide you every step of the way.
          </p>
          <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <Button 
              href="#contact" 
              variant="secondary" 
              size="lg" 
              icon={BookOpen}
              className="text-blue-800"
            >
              Start Your Journey
            </Button>
            <Button 
              href="#resources" 
              variant="outline" 
              size="lg" 
              icon={ArrowRight}
              className="border-white text-white hover:bg-white hover:text-blue-600"
            >
              Explore Resources
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CTA;