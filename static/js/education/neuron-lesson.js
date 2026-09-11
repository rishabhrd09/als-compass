/* Teaching sequence, deliberately slowed down. Values are illustrative, not clinical. */
(() => {
    'use strict';
    const clamp = value => Math.max(0, Math.min(1, value));
    const progress = (phase, start, end) => clamp((phase - start) / (end - start));
    const lesson = Object.freeze({
        cycleSeconds: 8,
        fiberCount: 5,
        // Two example contacts are lost. This count is not an ALS stage or estimate.
        connectionStrength(index, loss) {
            const amount = clamp(loss);
            return index === 1 || index === 3 ? 1 - amount * amount * (3 - 2 * amount) : 1;
        },
        frameAt(time) {
            const phase = ((time / 8) % 1 + 1) % 1;
            const muscleProgress = progress(phase, .8, .96);
            return {
                stage: phase < .65 ? 0 : phase < .8 ? 1 : 2,
                axonActive: phase >= .08 && phase < .5,
                axonProgress: progress(phase, .08, .5),
                terminalActive: phase >= .5 && phase < .65,
                terminalProgress: progress(phase, .5, .65),
                chemicalActive: phase >= .65 && phase < .8,
                chemicalProgress: progress(phase, .65, .8),
                contraction: phase >= .8 && phase < .96 ? Math.sin(muscleProgress * Math.PI) ** 2 : 0
            };
        }
    });
    if (typeof module !== 'undefined' && module.exports) module.exports = lesson;
    if (typeof window !== 'undefined') window.NeuronLesson = lesson;
})();
