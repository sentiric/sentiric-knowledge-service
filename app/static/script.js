document.addEventListener('DOMContentLoaded', () => {
    const queryForm = document.getElementById('query-form');
    queryForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);
        const requestData = Object.fromEntries(formData.entries());
        requestData.top_k = parseInt(requestData.top_k, 10);

        const resultContainer = document.getElementById('result-container');
        const resultDiv = document.getElementById('result-content');
        const errorMessage = document.getElementById('error-message');
        const spinner = document.getElementById('spinner');
        const submitBtn = document.getElementById('submit-btn');

        resultContainer.classList.remove('hidden');
        resultDiv.innerHTML = '';
        errorMessage.classList.add('hidden');
        spinner.classList.remove('hidden');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Sorgulanıyor...';

        try {
            const response = await fetch('/api/v1/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP hatası! Durum: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.results && data.results.length > 0) {
                data.results.forEach(res => {
                    const resultCard = document.createElement('div');
                    resultCard.className = 'result-card';
                    resultCard.innerHTML = `
                        <div class="score">Skor: ${res.score.toFixed(4)}</div>
                        <div class="source">Kaynak: ${res.payload.source}</div>
                        <pre>${res.payload.text}</pre>
                    `;
                    resultDiv.appendChild(resultCard);
                });
            } else {
                resultDiv.innerHTML = '<p>Bu sorgu için ilgili sonuç bulunamadı.</p>';
            }

        } catch (error) {
            console.error('Sorgu hatası:', error);
            errorMessage.textContent = `Hata: ${error.message}`;
            errorMessage.classList.remove('hidden');
        } finally {
            spinner.classList.add('hidden');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Sorgula';
        }
    });
});