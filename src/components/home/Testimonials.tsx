import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Star, Quote } from 'lucide-react';
import Container from '../ui/Container';
import SectionHeading from '../ui/SectionHeading';

interface TestimonialProps {
  quote: string;
  name: string;
  title: string;
  image: string;
}

const testimonials: TestimonialProps[] = [
  {
    quote: "The guidance and support I received from PathToJudaism made my conversion journey meaningful and transformative. The community welcomed me with open arms.",
    name: "Sarah Goldstein",
    title: "Converted in 2022",
    image: "https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg"
  },
  {
    quote: "As someone who had always felt drawn to Judaism, finding PathToJudaism was life-changing. The resources, classes, and mentorship helped me navigate the complexities of conversion.",
    name: "David Martinez",
    title: "Converted in 2021",
    image: "https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg"
  },
  {
    quote: "The rabbis and educators at PathToJudaism showed incredible patience and wisdom throughout my journey. I'm grateful to have found such a supportive community.",
    name: "Rebecca Chen",
    title: "Converted in 2023",
    image: "https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg"
  }
];

const Testimonials: React.FC = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const goToPrevious = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex === 0 ? testimonials.length - 1 : prevIndex - 1
    );
  };

  const goToNext = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex === testimonials.length - 1 ? 0 : prevIndex + 1
    );
  };

  return (
    <section id="testimonials" className="py-20 bg-white">
      <Container>
        <SectionHeading 
          title="Conversion Stories"
          subtitle="Hear from individuals who have completed their journey to Judaism through our guidance and support."
        />
        
        <div className="max-w-4xl mx-auto">
          <div className="relative bg-blue-50 rounded-xl p-8 md:p-12 shadow-lg">
            <div className="absolute -top-5 -left-5 text-blue-500">
              <Quote size={48} />
            </div>
            
            <div className="flex flex-col md:flex-row items-center space-y-8 md:space-y-0 md:space-x-8">
              <div className="w-24 h-24 md:w-32 md:h-32 rounded-full overflow-hidden flex-shrink-0 border-4 border-white shadow-md">
                <img 
                  src={testimonials[currentIndex].image} 
                  alt={testimonials[currentIndex].name} 
                  className="w-full h-full object-cover"
                />
              </div>
              
              <div>
                <p className="text-gray-700 italic text-lg mb-6">"{testimonials[currentIndex].quote}"</p>
                <div className="flex items-center">
                  <div>
                    <p className="font-semibold text-gray-900">{testimonials[currentIndex].name}</p>
                    <p className="text-blue-600">{testimonials[currentIndex].title}</p>
                  </div>
                  <div className="ml-auto flex">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="w-5 h-5 text-yellow-500 fill-current" />
                    ))}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex justify-between mt-8">
              <button 
                onClick={goToPrevious}
                className="w-10 h-10 rounded-full bg-white shadow-md flex items-center justify-center text-blue-600 hover:bg-blue-600 hover:text-white transition-colors"
                aria-label="Previous testimonial"
              >
                <ChevronLeft size={20} />
              </button>
              
              <div className="flex space-x-2">
                {testimonials.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentIndex(index)}
                    className={`w-3 h-3 rounded-full transition-colors ${
                      index === currentIndex ? 'bg-blue-600' : 'bg-gray-300'
                    }`}
                    aria-label={`Go to testimonial ${index + 1}`}
                  />
                ))}
              </div>
              
              <button 
                onClick={goToNext}
                className="w-10 h-10 rounded-full bg-white shadow-md flex items-center justify-center text-blue-600 hover:bg-blue-600 hover:text-white transition-colors"
                aria-label="Next testimonial"
              >
                <ChevronRight size={20} />
              </button>
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
};

export default Testimonials;