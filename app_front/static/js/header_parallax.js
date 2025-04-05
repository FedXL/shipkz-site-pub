document.addEventListener('scroll', function() {
    const image = document.querySelector('.image-container img');
    const scrollPosition = window.scrollY;

    // Измените значение 0.5 для настройки скорости перемещения изображения
    const translateY = scrollPosition * 0.5;
    image.style.transform = `translate(-50%, calc(-54% + ${translateY}px)) scale(0.75)`;
});