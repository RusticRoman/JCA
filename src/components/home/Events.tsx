import React from 'react';
import { Calendar as CalendarIcon, Clock, MapPin, Users } from 'lucide-react';
import Container from '../ui/Container';
import SectionHeading from '../ui/SectionHeading';
import Button from '../ui/Button';

interface EventProps {
  title: string;
  date: string;
  time: string;
  location: string;
  image: string;
  attendees: number;
  category: string;
}

const events: EventProps[] = [
  {
    title: "Introduction to Judaism Class",
    date: "October 15, 2025",
    time: "7:00 PM - 9:00 PM",
    location: "Jewish Community Center",
    image: "https://images.pexels.com/photos/3184306/pexels-photo-3184306.jpeg",
    attendees: 28,
    category: "Education"
  },
  {
    title: "Hebrew Reading Workshop",
    date: "October 22, 2025",
    time: "6:30 PM - 8:30 PM",
    location: "Online via Zoom",
    image: "https://images.pexels.com/photos/3183197/pexels-photo-3183197.jpeg",
    attendees: 15,
    category: "Language"
  },
  {
    title: "Shabbat Experience Dinner",
    date: "October 25, 2025",
    time: "6:00 PM - 9:00 PM",
    location: "Temple Beth Shalom",
    image: "https://images.pexels.com/photos/3184183/pexels-photo-3184183.jpeg",
    attendees: 42,
    category: "Community"
  }
];

const EventCard: React.FC<EventProps> = ({ title, date, time, location, image, attendees, category }) => {
  return (
    <div className="bg-white rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-all group">
      <div className="relative h-48 overflow-hidden">
        <div className="absolute top-4 left-4 z-10">
          <span className="bg-blue-600 text-white text-sm font-medium px-3 py-1 rounded-full">
            {category}
          </span>
        </div>
        <img 
          src={image} 
          alt={title} 
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
        />
      </div>
      
      <div className="p-6">
        <h3 className="text-xl font-semibold mb-3 text-gray-900">{title}</h3>
        
        <div className="space-y-3 mb-4">
          <div className="flex items-center text-gray-700">
            <CalendarIcon size={18} className="mr-2 text-blue-600" />
            <span>{date}</span>
          </div>
          
          <div className="flex items-center text-gray-700">
            <Clock size={18} className="mr-2 text-blue-600" />
            <span>{time}</span>
          </div>
          
          <div className="flex items-center text-gray-700">
            <MapPin size={18} className="mr-2 text-blue-600" />
            <span>{location}</span>
          </div>
        </div>
        
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
          <div className="flex items-center text-gray-700">
            <Users size={18} className="mr-2 text-blue-600" />
            <span>{attendees} Attendees</span>
          </div>
          
          <Button 
            href="#" 
            variant="secondary" 
            size="sm"
          >
            Register
          </Button>
        </div>
      </div>
    </div>
  );
};

const Events: React.FC = () => {
  return (
    <section id="events" className="py-20 bg-blue-50">
      <Container>
        <SectionHeading 
          title="Upcoming Events"
          subtitle="Join us for classes, workshops, and community gatherings to deepen your knowledge and connection."
        />
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {events.map((event, index) => (
            <EventCard key={index} {...event} />
          ))}
        </div>
        
        <div className="mt-12 text-center">
          <Button 
            href="#" 
            variant="primary"
            icon={CalendarIcon}
          >
            View All Events
          </Button>
        </div>
      </Container>
    </section>
  );
};

export default Events;