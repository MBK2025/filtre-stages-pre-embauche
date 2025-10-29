// Se lance quand le HTML est prêt
document.addEventListener('DOMContentLoaded', () => {
    const listeContainer = document.getElementById('liste-stages');
    const loadingIndicator = document.getElementById('loading');

    // On va chercher notre fichier JSON généré par le robot
    // On ajoute un cache-buster pour toujours avoir la version la plus fraîche
    fetch(`stages_filtres.json?v=${new Date().getTime()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Erreur réseau ou fichier non trouvé");
            }
            return response.json();
        })
        .then(stages => {
            // On cache le message "Chargement"
            loadingIndicator.style.display = 'none';
            
            if (stages.length === 0) {
                listeContainer.innerHTML = "<p>Aucun stage de pré-embauche trouvé récemment. Revenez demain !</p>";
                return;
            }

            // Pour chaque stage trouvé, on crée une "carte" HTML
            stages.forEach(stage => {
                const stageElement = document.createElement('div');
                stageElement.classList.add('stage-carte');

                stageElement.innerHTML = `
                    <h3>${stage.titre}</h3>
                    <p class="entreprise">${stage.entreprise}</p>
                    <p class="lieu">${stage.lieu}</p>
                    <a href="${stage.url}" target="_blank" rel="noopener noreferrer">Voir l'offre</a>
                `;

                listeContainer.appendChild(stageElement);
            });
        })
        .catch(error => {
            // En cas d'erreur
            loadingIndicator.style.display = 'none';
            listeContainer.innerHTML = `<p style="color: red;">Erreur lors du chargement des offres : ${error.message}</p>`;
            console.error("Erreur:", error);
        });
});