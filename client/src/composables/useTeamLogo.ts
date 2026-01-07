import { ref, computed } from 'vue';
import { useKplStore } from '@/stores/kpl';


export function useTeamLogo(teamId: string, initialLogoUrl?: string) {
    const kplStore = useKplStore();
    const currentLogoUrl = ref(initialLogoUrl || '');
    const hasError = ref(false);

    const standingsLogo = computed(() => {
        const standing = kplStore.standings.find(s => s.team.id === teamId);
        return standing?.team.logo_url || '';
    });

    const logoUrl = computed(() => {
        if (!hasError.value && currentLogoUrl.value) {
            return currentLogoUrl.value;
        }
        return standingsLogo.value || currentLogoUrl.value || '';
    });

    const handleError = () => {
        if (!hasError.value && standingsLogo.value && standingsLogo.value !== currentLogoUrl.value) {
            hasError.value = true;
            currentLogoUrl.value = standingsLogo.value;
        }
    };

    const resetError = () => {
        hasError.value = false;
    };

    return {
        logoUrl,
        handleError,
        resetError,
        hasError
    };
}


export function getTeamLogoFromStandings(teamIdOrName: string, standings: any[]): string {
    const standing = standings.find(
        s => s.team.id === teamIdOrName || s.team.name === teamIdOrName
    );
    return standing?.team.logo_url || '';
}

export function getFallbackLogoUrl(teamId: string): string {
    const kplStore = useKplStore();
    const standingsLogo = kplStore.standings.find(s => s.team.id === teamId)?.team.logo_url;

    if (standingsLogo) {
        return standingsLogo;
    }

    return createPlaceholderLogo();
}


function createPlaceholderLogo(): string {
    const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="45" fill="#e5e7eb"/>
      <path d="M50 30 L70 60 L50 55 L30 60 Z" fill="#9ca3af"/>
    </svg>
  `;
    return `data:image/svg+xml;base64,${btoa(svg)}`;
}
