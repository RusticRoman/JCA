import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import Container from '../ui/Container';
import SectionHeading from '../ui/SectionHeading';

interface FAQItemProps {
  question: string;
  answer: string;
  isOpen: boolean;
  toggleOpen: () => void;
}

const FAQItem: React.FC<FAQItemProps> = ({ 
  question, 
  answer, 
  isOpen, 
  toggleOpen 
}) => {
  return (
    <div className="border-b border-gray-200 py-5">
      <button
        className="flex w-full justify-between items-center text-left focus:outline-none"
        onClick={toggleOpen}
        aria-expanded={isOpen}
      >
        <h3 className="text-lg font-medium text-gray-900">{question}</h3>
        <span className="ml-6 flex-shrink-0">
          {isOpen ? (
            <ChevronUp className="h-5 w-5 text-blue-500" />
          ) : (
            <ChevronDown className="h-5 w-5 text-gray-500" />
          )}
        </span>
      </button>
      
      <div className={`mt-2 overflow-hidden transition-all duration-300 ${isOpen ? 'max-h-96' : 'max-h-0'}`}>
        <p className="text-gray-600">{answer}</p>
      </div>
    </div>
  );
};

const FAQ: React.FC = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(0);
  
  const faqs = [
    {
      question: "What is the process for converting to Judaism?",
      answer: "The process of conversion to Judaism typically involves studying Jewish texts, laws, customs, and history; regular attendance at synagogue services; becoming part of a Jewish community; learning some Hebrew; and meeting regularly with a rabbi. The process culminates in appearing before a Beit Din (rabbinic court), immersion in a mikvah (ritual bath), and for men, circumcision or a symbolic circumcision if already circumcised. The length of the process varies but typically takes at least a year."
    },
    {
      question: "Do I need to learn Hebrew to convert?",
      answer: "While complete fluency in Hebrew is not typically required for conversion, learning the basics of Hebrew is an important part of the conversion process. This includes being able to read Hebrew letters and basic prayers. The level of Hebrew proficiency expected may vary depending on the branch of Judaism and the specific rabbi or community guiding your conversion."
    },
    {
      question: "Which denomination of Judaism should I choose for conversion?",
      answer: "Judaism has several major denominations, including Orthodox, Conservative, Reform, and Reconstructionist, each with different approaches to Jewish law and tradition. The choice depends on your personal beliefs, lifestyle, and the Jewish community you feel most connected to. Our organization can help you explore the different denominations and connect with rabbis from various movements to find the best fit for your spiritual journey."
    },
    {
      question: "Will my conversion be recognized by all Jews?",
      answer: "Recognition of conversions varies among different Jewish denominations. Generally, Orthodox conversions are recognized by all denominations, while conversions through Reform or Conservative Judaism may not be recognized by Orthodox communities. It's important to discuss this with your rabbi early in the process if universal recognition is important to you."
    },
    {
      question: "What is the cost associated with conversion to Judaism?",
      answer: "Costs can vary widely depending on your location, the synagogue, and the rabbi. Typical expenses may include classes, books, synagogue membership, ritual items, and possibly a fee for the Beit Din and mikvah. Some communities offer financial assistance for those in need. We believe that financial constraints should not be a barrier to conversion, and we can help you find programs that work within your budget."
    },
    {
      question: "Can I attend services and classes if I'm still exploring and haven't committed to conversion?",
      answer: "Absolutely! Most synagogues and Jewish communities welcome those who are exploring Judaism. Attending services, classes, and community events is encouraged as part of the exploration process. This gives you an opportunity to experience Jewish life firsthand and determine if conversion is right for you."
    }
  ];
  
  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section id="faq" className="py-20 bg-white">
      <Container>
        <SectionHeading 
          title="Frequently Asked Questions"
          subtitle="Find answers to common questions about conversion to Judaism and our support process."
        />
        
        <div className="max-w-3xl mx-auto">
          {faqs.map((faq, index) => (
            <FAQItem 
              key={index}
              question={faq.question}
              answer={faq.answer}
              isOpen={openIndex === index}
              toggleOpen={() => toggleFAQ(index)}
            />
          ))}
        </div>
        
        <div className="text-center mt-12">
          <p className="text-gray-700 mb-4">
            Don't see your question here? Feel free to reach out to us directly.
          </p>
          <a 
            href="#contact" 
            className="text-blue-600 font-medium hover:text-blue-800"
          >
            Contact us for more information
          </a>
        </div>
      </Container>
    </section>
  );
};

export default FAQ;