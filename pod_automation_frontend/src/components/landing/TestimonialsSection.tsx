import React from 'react';

// Placeholder data
const testimonials = [
  {
    quote: 'Saved me hours! The AI suggestions are spot on.',
    name: 'Jane D.',
    shop: 'Crafty Creations Co.',
    // photo: '/path/to/photo1.jpg' // Placeholder for image path
  },
  {
    quote: 'My sales increased after using the AI-generated designs. Highly recommend!',
    name: 'Mike P.',
    shop: 'Pixel Perfect Prints',
    // photo: '/path/to/photo2.jpg'
  },
  {
    quote: 'This is a must-have tool for any serious Etsy POD seller. Game changer!',
    name: 'Sarah L.',
    shop: 'Unique Tee Boutique',
    // photo: '/path/to/photo3.jpg'
  },
];

const TestimonialsSection: React.FC = () => {
  return (
    <section className="py-16 bg-light-bg dark:bg-dark-card">
      <div className="container mx-auto px-6 text-center">
        <h2 className="text-3xl font-bold text-light-text dark:text-dark-text mb-12">
          Loved by Etsy Sellers Like You
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((testimonial) => (
            <div key={testimonial.name} className="bg-white dark:bg-dark-bg p-6 rounded-lg shadow-md">
              {/* Placeholder for photo */}
              <div className="w-16 h-16 rounded-full bg-gray-300 dark:bg-dark-border mx-auto mb-4 flex items-center justify-center">
                <span className="text-gray-500 dark:text-dark-text-secondary text-xs">Photo</span>
              </div>
              <p className="italic text-light-text-secondary dark:text-dark-text-secondary mb-4">"{testimonial.quote}"</p>
              <p className="font-semibold text-light-text dark:text-dark-text">- {testimonial.name}, {testimonial.shop}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default TestimonialsSection;

