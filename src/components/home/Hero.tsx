import React from 'react';
import { BookOpen, ArrowRight } from 'lucide-react';
import Button from '../ui/Button';

const Hero: React.FC = () => {
  return (
    <section id="home" className="relative pt-20 pb-32 lg:pb-40 bg-gradient-to-r from-blue-50 to-blue-100 overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 z-0 opacity-25">
        <div className="absolute -top-40 -right-40 w-80 h-80 rounded-full bg-blue-300"></div>
        <div className="absolute top-60 -left-20 w-60 h-60 rounded-full bg-blue-200"></div>
        <div className="absolute bottom-0 right-20 w-40 h-40 rounded-full bg-blue-200"></div>
      </div>
      
      <div className="container mx-auto px-4 md:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="text-center lg:text-left">
            <div className="inline-block px-4 py-2 rounded-full bg-blue-100 text-blue-700 font-medium text-sm mb-6 animate-fade-in">
              Begin Your Spiritual Journey
            </div>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              Discover Your Path <br />
              <span className="text-blue-600">to Judaism</span>
            </h1>
            <p className="text-lg md:text-xl text-gray-700 mb-8 max-w-lg mx-auto lg:mx-0">
              We guide individuals on their unique journey toward embracing Jewish faith, traditions, and community with compassion and wisdom.
            </p>
            <div className="flex flex-col sm:flex-row justify-center lg:justify-start space-y-4 sm:space-y-0 sm:space-x-4">
              <Button 
                href="#contact" 
                variant="primary" 
                size="lg" 
                icon={BookOpen}
              >
                Start Your Journey
              </Button>
              <Button 
                href="#resources" 
                variant="outline" 
                size="lg" 
                icon={ArrowRight}
              >
                Explore Resources
              </Button>
            </div>
          </div>
          
          <div className="relative">
            <div className="absolute inset-0 bg-blue-200 rounded-lg transform rotate-3"></div>
            <div className="relative overflow-hidden rounded-lg shadow-xl transform transition-all hover:scale-105 duration-300">
              <img 
                src="https://images.pexels.com/photos/3958426/pexels-photo-3958426.jpeg" 
                alt="Jewish family celebrating Shabbat dinner" 
                className="w-full h-auto object-cover"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;