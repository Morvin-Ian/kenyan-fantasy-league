<template>
    <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div class="max-w-7xl mt-4 mx-auto flex flex-col lg:flex-row gap-6">
            <!-- Main Content (Field) -->
            <div class="w-full lg:w-2/3 bg-white rounded-xl shadow-lg">
                <Pitch
                    :goalkeeper="goalkeeper"
                    :defenders="defenders"
                    :midfielders="midfielders"
                    :forwards="forwards"
                    :switch-source="switchSource"
                    :switch-active="switchActive"
                    @player-click="handlePlayerClick"
                />

                <Bench
                    :bench-players="benchPlayers"
                    :switch-source="switchSource"
                    :switch-active="switchActive"
                    @player-click="handlePlayerClick"
                />
            </div>

            <!-- Sidebar -->
            <Sidebar
                :total-points="totalPoints"
                :average-points="averagePoints"
                :highest-points="highestPoints"
                :overall-rank="overallRank"
                :upcoming-fixtures="upcomingFixtures"
                :recent-results="recentResults"
                :top-performers="topPerformers"
            />
        </div>

        <!-- Player Management Modal -->
        <PlayerModal
            :show-modal="showModal"
            :selected-player="selectedPlayer"
            @close-modal="closeModal"
            @initiate-switch="initiateSwitch"
            @make-captain="makeCaptain"
            @make-vice-captain="makeViceCaptain"
        />
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import Pitch from "@/components/Team/Pitch.vue";
import Bench from "@/components/Team/Bench.vue";
import Sidebar from "@/components/Team/SideBar.vue";
import PlayerModal from "@/components/Team/PlayerModal.vue";
import { startingEleven, benchPlayers } from "@/helpers/data";
import { Player, Fixture, Result, Performer } from "@/helpers/types/team";

// State
const showModal = ref(false);
const selectedPlayer = ref<Player | null>(null);
const switchActive = ref(false);
const switchSource = ref<Player | null>(null);
const isBenchSwitch = ref(false);

const totalPoints = ref(57);
const averagePoints = ref(52);
const highestPoints = ref(121);
const overallRank = ref("234,567");

const upcomingFixtures = ref<Fixture[]>([
    { match: "Black Stone FC vs Yellow Wolves", date: "20 Feb 2024" },
    { match: "Black Stone FC vs Silver Sharks", date: "25 Feb 2024" },
]);

const recentResults = ref<Result[]>([
    { match: "Black Stone FC 2-1 Red Devils", date: "15 Feb 2024" },
    { match: "Black Stone FC 3-0 Blue Tigers", date: "10 Feb 2024" },
    { match: "Black Stone FC 1-1 Green Eagles", date: "5 Feb 2024" },
]);

const topPerformers = ref<Performer[]>([
    { name: "E. Olunga", points: 15, image: "https://example.com/player1.png" },
    {
        name: "V. Manyara",
        points: 12,
        image: "https://example.com/player2.png",
    },
    { name: "B. Peter", points: 10, image: "https://example.com/player3.png" },
]);

const startingElevenRef = ref(startingEleven);
const benchPlayersRef = ref(benchPlayers);

const goalkeeper = computed(() => startingElevenRef.value.goalkeeper);
const defenders = computed(() => startingElevenRef.value.defenders);
const midfielders = computed(() => startingElevenRef.value.midfielders);
const forwards = computed(() => startingElevenRef.value.forwards);

const openPlayerModal = (player: Player) => {
    selectedPlayer.value = player;
    showModal.value = true;
};

const closeModal = () => {
    showModal.value = false;
    selectedPlayer.value = null;
};

const handlePlayerClick = (player: Player, isBench = false) => {
    if (switchActive.value) {
        performSwitch(player, isBench);
    } else {
        openPlayerModal(player);
    }
};

const initiateSwitch = () => {
    if (!selectedPlayer.value) {
        console.warn("No player selected for switching.");
        return;
    }
    switchSource.value = selectedPlayer.value;
    switchActive.value = true;
    isBenchSwitch.value = benchPlayersRef.value.some(
        (p) => p.id === selectedPlayer.value?.id,
    );
    closeModal();
};

const performSwitch = (targetPlayer: Player, isBench: boolean) => {
    const sourcePlayer = switchSource.value;

    if (!sourcePlayer) return;

    if (isBenchSwitch.value === isBench) {
        return;
    }

    const getFormationCounts = () => {
        return {
            DEF: startingElevenRef.value.defenders.length,
            MID: startingElevenRef.value.midfielders.length,
            FWD: startingElevenRef.value.forwards.length,
        };
    };

    const getTotalFieldPlayers = () => {
        const counts = getFormationCounts();
        return counts.DEF + counts.MID + counts.FWD + 1; // +1 for goalkeeper
    };

    const isValidFormationChange = (sourcePos: string, targetPos: string) => {
        if (sourcePos === "GK" || targetPos === "GK") {
            return false; // Goalkeepers can only switch with goalkeepers
        }

        const currentCounts = getFormationCounts();
        const newCounts = { ...currentCounts };

        if (isBenchSwitch.value) {
            newCounts[targetPos]--;
            newCounts[sourcePos]++;
        } else {
            newCounts[sourcePos]--;
            newCounts[targetPos]++;
        }

        // formation constraints
        const constraints = {
            DEF: { min: 3, max: 5 },
            MID: { min: 3, max: 5 },
            FWD: { min: 1, max: 3 },
        };

        return Object.entries(newCounts).every(([pos, count]) => {
            return (
                count >= constraints[pos].min && count <= constraints[pos].max
            );
        });
    };

    if (isBenchSwitch.value) {
        const benchIndex = benchPlayersRef.value.findIndex(
            (p) => p.id === sourcePlayer.id,
        );

        if (targetPlayer.position === sourcePlayer.position) {
            if (targetPlayer.position === "GK") {
                const tempGK = startingElevenRef.value.goalkeeper;
                startingElevenRef.value.goalkeeper = sourcePlayer;
                benchPlayersRef.value[benchIndex] = tempGK;
            } else {
                const positionArray = getPositionArray(targetPlayer.position);
                const fieldIndex = positionArray.findIndex(
                    (p) => p.id === targetPlayer.id,
                );

                if (fieldIndex !== -1) {
                    const tempPlayer = positionArray[fieldIndex];
                    positionArray[fieldIndex] = sourcePlayer;
                    benchPlayersRef.value[benchIndex] = tempPlayer;
                }
            }
        } else {
            if (
                !isValidFormationChange(
                    sourcePlayer.position,
                    targetPlayer.position,
                )
            ) {
                console.warn(
                    "Invalid formation change. Must maintain valid formation constraints.",
                );
                return;
            }

            const targetPosArray = getPositionArray(targetPlayer.position);
            const fieldIndex = targetPosArray.findIndex(
                (p) => p.id === targetPlayer.id,
            );

            if (fieldIndex !== -1) {
                targetPosArray.splice(fieldIndex, 1);

                const sourcePosArray = getPositionArray(sourcePlayer.position);
                sourcePosArray.push(sourcePlayer);

                benchPlayersRef.value[benchIndex] = targetPlayer;
            }
        }
    } else {
        const benchIndex = benchPlayersRef.value.findIndex(
            (p) => p.id === targetPlayer.id,
        );

        if (sourcePlayer.position === targetPlayer.position) {
            if (sourcePlayer.position === "GK") {
                const tempGK = startingElevenRef.value.goalkeeper;
                startingElevenRef.value.goalkeeper = targetPlayer;
                benchPlayersRef.value[benchIndex] = tempGK;
            } else {
                const positionArray = getPositionArray(sourcePlayer.position);
                const fieldIndex = positionArray.findIndex(
                    (p) => p.id === sourcePlayer.id,
                );

                if (fieldIndex !== -1) {
                    const tempPlayer = positionArray[fieldIndex];
                    positionArray[fieldIndex] = targetPlayer;
                    benchPlayersRef.value[benchIndex] = tempPlayer;
                }
            }
        } else {
            if (
                !isValidFormationChange(
                    sourcePlayer.position,
                    targetPlayer.position,
                )
            ) {
                console.warn(
                    "Invalid formation change. Must maintain valid formation constraints.",
                );
                return;
            }

            const sourcePosArray = getPositionArray(sourcePlayer.position);
            const fieldIndex = sourcePosArray.findIndex(
                (p) => p.id === sourcePlayer.id,
            );

            if (fieldIndex !== -1) {
                sourcePosArray.splice(fieldIndex, 1);

                const targetPosArray = getPositionArray(targetPlayer.position);
                targetPosArray.push(targetPlayer);

                benchPlayersRef.value[benchIndex] = sourcePlayer;
            }
        }
    }

    if (getTotalFieldPlayers() !== 11) {
        console.error("Invalid total number of players");
        return;
    }

    switchActive.value = false;
    switchSource.value = null;
    isBenchSwitch.value = false;
};

const getPositionArray = (position: "DEF" | "MID" | "FWD") => {
    return startingElevenRef.value[
        position.toLowerCase() as keyof typeof startingElevenRef.value
    ];
};

const isPlayerInStartingEleven = (player: Player) => {
    if (!player) return false;

    if (startingElevenRef.value.goalkeeper.id === player.id) {
        return true;
    }

    return ["defenders", "midfielders", "forwards"].some((position) => {
        return startingElevenRef.value[position].some(
            (p: Player) => p.id === player.id,
        );
    });
};

const findCurrentCaptain = () => {
    const positions = ["defenders", "midfielders", "forwards"];
    for (const position of positions) {
        const player = startingElevenRef.value[position].find(
            (p) => p.isCaptain,
        );
        if (player) return player;
    }
    if (startingElevenRef.value.goalkeeper.isCaptain) {
        return startingElevenRef.value.goalkeeper;
    }
    return null;
};

const findCurrentViceCaptain = () => {
    const positions = ["defenders", "midfielders", "forwards"];
    for (const position of positions) {
        const player = startingElevenRef.value[position].find(
            (p) => p.isViceCaptain,
        );
        if (player) return player;
    }
    // Check goalkeeper
    if (startingElevenRef.value.goalkeeper.isViceCaptain) {
        return startingElevenRef.value.goalkeeper;
    }
    return null;
};

const clearCaptaincy = () => {
    const positions = ["goalkeeper", "defenders", "midfielders", "forwards"];
    positions.forEach((position) => {
        const players =
            position === "goalkeeper"
                ? [startingElevenRef.value.goalkeeper]
                : startingElevenRef.value[position];
        players.forEach((player) => {
            player.isCaptain = false;
        });
    });
};

const clearViceCaptaincy = () => {
    const positions = ["goalkeeper", "defenders", "midfielders", "forwards"];
    positions.forEach((position) => {
        const players =
            position === "goalkeeper"
                ? [startingElevenRef.value.goalkeeper]
                : startingElevenRef.value[position];
        players.forEach((player) => {
            player.isViceCaptain = false;
        });
    });
};

const makeCaptain = () => {
    if (!selectedPlayer.value) {
        console.warn("No player selected to be captain.");
        return;
    }

    if (!isPlayerInStartingEleven(selectedPlayer.value)) {
        console.warn("Cannot assign captaincy to a bench player.");
        return;
    }

    if (selectedPlayer.value.isCaptain) {
        console.warn(`${selectedPlayer.value.name} is already the captain.`);
        return;
    }

    clearCaptaincy();
    selectedPlayer.value.isCaptain = true;
    closeModal();
};

const makeViceCaptain = () => {
    if (!selectedPlayer.value) {
        console.warn("No player selected to be vice-captain.");
        return;
    }

    if (!isPlayerInStartingEleven(selectedPlayer.value)) {
        console.warn("Cannot assign vice-captaincy to a bench player.");
        return;
    }

    if (selectedPlayer.value.isViceCaptain) {
        console.warn(
            `${selectedPlayer.value.name} is already the vice-captain.`,
        );
        return;
    }

    clearViceCaptaincy();
    selectedPlayer.value.isViceCaptain = true;
    console.log(`${selectedPlayer.value.name} is now the vice-captain.`);
    closeModal();
};
</script>
