
    const slides = document.getElementById('slides');
    const next = document.getElementById('next');
    const prev = document.getElementById('prev');
    const dots = document.querySelectorAll('#dots span');

    let index = 0;
    const total = slides.children.length;

     const navbar = document.getElementById("mainNavbar");
  let scrollTimeout;

  window.addEventListener("scroll", () => {
    // Hide navbar while scrolling
    navbar.classList.add("-translate-y-full");

    clearTimeout(scrollTimeout);

    // Show navbar again when scrolling stops
    scrollTimeout = setTimeout(() => {
      navbar.classList.remove("-translate-y-full");
    }, 400);
  });

    function updateCarousel() {
      const slideWidth = slides.children[0].offsetWidth + 24; // include mx-3
      slides.style.transform = `translateX(-${index * slideWidth}px)`;
      dots.forEach((dot, i) => dot.classList.toggle('bg-purple-700', i === index));
    }

    next.addEventListener('click', () => {
      index = (index + 1) % total;
      updateCarousel();
    });

    prev.addEventListener('click', () => {
      index = (index - 1 + total) % total;
      updateCarousel();
    });

    updateCarousel();

    document.addEventListener("DOMContentLoaded", () => {
      const panels = document.querySelectorAll('.panel');
      panels.forEach(panel => {
        panel.addEventListener('click', () => {
          panel.classList.toggle('bg-purple-50');
        });
      });
    });

    // Select all technology items
    document.querySelectorAll('.tech-item img').forEach((icon, index) => {
      icon.addEventListener('mouseenter', () => {
        // Alternate animations for fun
        if (index % 2 === 0) {
          icon.classList.add('bounce');
        } else {
          icon.classList.add('spin');
        }
      });

      icon.addEventListener('animationend', () => {
        // Remove animation class so it can trigger again on hover
        icon.classList.remove('bounce', 'spin');
      });
    });

const cards = document.querySelectorAll('.team-card');
  const modal = document.getElementById('team-modal');
  const closeModal = document.getElementById('close-modal');

  const modalImg = document.getElementById('modal-img');
  const modalName = document.getElementById('modal-name');
  const modalRole = document.getElementById('modal-role');
  const modalText = document.getElementById('modal-text');

  cards.forEach(card => {
    card.addEventListener('click', () => {
      modalImg.src = card.dataset.img;
      modalName.textContent = card.dataset.name;
      modalRole.textContent = card.dataset.role;
      modalText.textContent = card.dataset.text;
      modal.classList.remove('hidden');
    });
  });


  closeModal.addEventListener('click', () => {
    modal.classList.add('hidden');
  });

  
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.classList.add('hidden');
    }
  });
