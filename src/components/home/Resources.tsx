import React from 'react';
import { Book, Video, Calendar, Download, ArrowRight } from 'lucide-react';
import Container from '../ui/Container';
import SectionHeading from '../ui/SectionHeading';
import Button from '../ui/Button';

interface ResourceCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  href: string;
  color: string;
}

const ResourceCard: React.FC<ResourceCardProps> = ({ icon, title, description, href, color }) => {
  return (
    <div className={`rounded-lg overflow-hidden shadow-md transition-all hover:shadow-lg hover:-translate-y-1 bg-white border-t-4 ${color}`}>
      <div className="p-6">
        <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-4 ${color.replace('border', 'bg')}`}>
          {icon}
        </div>
        <h3 className="text-xl font-semibold mb-3 text-gray-900">{title}</h3>
        <p className="text-gray-600 mb-4">{description}</p>
        <a 
          href={href} 
          className="inline-flex items-center font-medium text-blue-600 hover:text-blue-800"
        >
          Learn More <ArrowRight size={16} className="ml-1" />
        </a>
      </div>
    </div>
  );
};

const Resources: React.FC = () => {
  const resources = [
    {
      icon: <Book className="text-blue-600" size={24} />,
      title: "Judaism 101",
      description: "Introduction to Jewish beliefs, customs, holidays, and lifecycle events.",
      href: "#",
      color: "border-blue-600"
    },
    {
      icon: <Calendar className="text-purple-600" size={24} />,
      title: "The Conversion Process",
      description: "A step-by-step guide to the conversion journey and what to expect.",
      href: "#",
      color: "border-purple-600"
    },
    {
      icon: <Book className="text-green-600" size={24} />,
      title: "Hebrew Learning",
      description: "Resources for learning Hebrew, from beginner to advanced levels.",
      href: "#",
      color: "border-green-600"
    },
    {
      icon: <Video className="text-red-600" size={24} />,
      title: "Video Lectures",
      description: "Educational videos on various aspects of Jewish traditions and practices.",
      href: "#",
      color: "border-red-600"
    },
    {
      icon: <Calendar className="text-yellow-600" size={24} />,
      title: "Jewish Calendar",
      description: "Understanding the Jewish calendar, holidays, and observances.",
      href: "#",
      color: "border-yellow-600"
    },
    {
      icon: <Download className="text-indigo-600" size={24} />,
      title: "Study Materials",
      description: "Downloadable guides, worksheets, and reference materials for your journey.",
      href: "#",
      color: "border-indigo-600"
    }
  ];

  return (
    <section id="resources" className="py-20 bg-gray-50">
      <Container>
        <SectionHeading 
          title="Educational Resources"
          subtitle="Explore our collection of learning materials to guide you on your journey to Judaism."
        />
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {resources.map((resource, index) => (
            <ResourceCard 
              key={index}
              icon={resource.icon}
              title={resource.title}
              description={resource.description}
              href={resource.href}
              color={resource.color}
            />
          ))}
        </div>
        
        <div className="mt-12 text-center">
          <Button href="#contact" variant="primary">
            Request Additional Resources
          </Button>
        </div>
      </Container>
    </section>
  );
};

export default Resources;