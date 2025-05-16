import React from 'react';
import { Heart, Users, Book, Star } from 'lucide-react';
import Container from '../ui/Container';
import SectionHeading from '../ui/SectionHeading';

interface ValueCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

const ValueCard: React.FC<ValueCardProps> = ({ icon, title, description }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md transition-all hover:shadow-lg border border-gray-100">
      <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center mb-5 text-blue-600">
        {icon}
      </div>
      <h3 className="text-xl font-semibold mb-3 text-gray-900">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
};

const About: React.FC = () => {
  const values = [
    {
      icon: <Heart size={28} />,
      title: "Compassion",
      description: "We approach each individual's journey with understanding, empathy, and respect for their unique path."
    },
    {
      icon: <Users size={28} />,
      title: "Community",
      description: "We foster a supportive environment where connections are built and traditions are shared together."
    },
    {
      icon: <Book size={28} />,
      title: "Education",
      description: "We provide deep, meaningful learning experiences rooted in Jewish texts, history, and traditions."
    },
    {
      icon: <Star size={28} />,
      title: "Authenticity",
      description: "We honor the richness and diversity of Jewish practices while maintaining core traditions."
    }
  ];

  return (
    <section id="about" className="py-20 bg-white">
      <Container>
        <SectionHeading 
          title="Our Mission & Values"
          subtitle="We are dedicated to providing guidance, education, and community for those exploring or embracing Judaism."
        />
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
          <div>
            <p className="text-lg text-gray-700 mb-6">
              PathToJudaism was founded to create a welcoming, supportive environment for individuals interested in exploring and embracing Jewish faith and traditions. We recognize that the journey to Judaism is deeply personal and unique for each person.
            </p>
            <p className="text-lg text-gray-700 mb-6">
              Our team of rabbis, educators, and community leaders are committed to providing authentic, inclusive guidance throughout the conversion process and beyond, helping each person find their place within the rich tapestry of Jewish life.
            </p>
            <p className="text-lg text-gray-700">
              Whether you're just beginning to explore Judaism or you're already on your conversion journey, we're here to support you every step of the way with resources, community, and compassionate guidance.
            </p>
          </div>
          
          <div className="relative">
            <div className="absolute -top-6 -left-6 w-24 h-24 bg-blue-100 rounded-lg z-0"></div>
            <div className="absolute -bottom-6 -right-6 w-24 h-24 bg-blue-200 rounded-lg z-0"></div>
            <img 
              src="https://images.pexels.com/photos/7613561/pexels-photo-7613561.jpeg" 
              alt="Rabbi teaching a class" 
              className="rounded-lg w-full h-auto object-cover shadow-lg relative z-10"
            />
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mt-20">
          {values.map((value, index) => (
            <ValueCard 
              key={index}
              icon={value.icon}
              title={value.title}
              description={value.description}
            />
          ))}
        </div>
      </Container>
    </section>
  );
};

export default About;