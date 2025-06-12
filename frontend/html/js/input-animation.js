document.querySelectorAll('.input-box').forEach(box => {
    
    const input = box.querySelector('.password-input');
    const openEye = box.querySelector('.open-eye');
    const closedEye = box.querySelector('.closed-eye');
    const lockIcon = box.querySelector('.lock-icon');

    if (!input || !openEye || !closedEye) return;

    const togglePassword = () => {
        if (input.type === 'password') {
            input.type = 'text';
            openEye.classList.add('active');
            closedEye.classList.remove('active');
            lockIcon.classList.remove('active');
        } else {
            input.type = 'password';
            openEye.classList.remove('active');
            closedEye.classList.add('active');
            lockIcon.classList.remove('active');
        }
    };
    openEye.classList.remove('active');
    closedEye.classList.remove('active');
    const update = () => {
        const filled = input.value.trim() !== '';
        input.classList.toggle('filled', filled);

        if (filled || document.activeElement === input) {
            lockIcon.style.visibility = 'hidden';
            if (input.type === 'password') {
                closedEye.classList.add('active');
                openEye.classList.remove('active');
            } else {
                openEye.classList.add('active');
                closedEye.classList.remove('active');
            }
        } else {
            // input is empty and blurred
            lockIcon.style.visibility = 'visible';
            openEye.classList.remove('active');
            closedEye.classList.remove('active');
        }
    };
    
    update();
    
    input.addEventListener('input', update);
    input.addEventListener('focus', update);
    input.addEventListener('blur', update);
    
    
    closedEye.addEventListener('click', togglePassword);
    openEye.addEventListener('click', togglePassword);
    

});