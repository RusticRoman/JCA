import React from 'react';
import Hero from '../components/home/Hero';
import About from '../components/home/About';
import Resources from '../components/home/Resources';
import Testimonials from '../components/home/Testimonials';
import Events from '../components/home/Events';
import FAQ from '../components/home/FAQ';
import Contact from '../components/home/Contact';
import CTA from '../components/home/CTA';

const Home: React.FC = () => {
  return (
    <>
      <Hero />
      <About />
      <Resources />
      <Testimonials />
      <Events />
      <FAQ />
      <CTA />
      <Contact />
    </>
  );
};

export default Home;