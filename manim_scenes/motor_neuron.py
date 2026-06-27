"""
ALS Motor Neuron Animation — Manim Community Edition
Renders a cinematic educational animation showing:
  1. Healthy motor neuron anatomy & signal transmission
  2. Progressive ALS degeneration (3 stages)
  3. Side-by-side comparison

Usage:
  manim -qh --format=webm manim_scenes/motor_neuron.py MotorNeuronALS
  (or run render_animations.bat)
"""
from manim import *
import numpy as np

# ── Color palette (matches ALS Compass hero) ──
TEAL       = "#2dd4bf"
PURPLE     = "#a78bfa"
AMBER      = "#fbbf24"
DARK_BG    = "#0c0e16"
ALS_ORANGE = "#ff9966"
ALS_RED    = "#ff3333"
ALS_DARK   = "#662222"
MUSCLE_CLR = "#ffaa00"
MUTED      = "#8b92a5"


def create_neuron_group(x_offset=0, color=TEAL, label_suffix=""):
    """Build a complete motor neuron as a VGroup with named sub-parts."""

    soma_pos = np.array([x_offset - 3.2, 0, 0])

    # ── Dendrites ──
    dendrites = VGroup()
    branch_data = [
        (UP * 1.1 + LEFT * 1.4,  UP * 0.4 + LEFT * 0.8),
        (UP * 0.5 + LEFT * 1.6,  UP * 0.9 + LEFT * 1.0),
        (DOWN * 0.7 + LEFT * 1.5, DOWN * 0.3 + LEFT * 0.9),
        (DOWN * 1.2 + LEFT * 1.3, DOWN * 0.9 + LEFT * 0.7),
        (UP * 1.5 + LEFT * 1.0,  None),
        (DOWN * 1.5 + LEFT * 0.9, None),
    ]
    for offset, sub_offset in branch_data:
        line = Line(
            soma_pos + LEFT * 0.35,
            soma_pos + offset,
            stroke_color=color, stroke_width=2.5
        )
        dendrites.add(line)
        if sub_offset is not None:
            mid = (soma_pos + LEFT * 0.35 + soma_pos + offset) / 2
            sub = Line(mid, soma_pos + sub_offset + offset * 0.3,
                       stroke_color=color, stroke_width=1.5, stroke_opacity=0.6)
            dendrites.add(sub)

    # ── Soma ──
    soma = Circle(
        radius=0.45, fill_color="#005577", fill_opacity=1,
        stroke_color=color, stroke_width=2.5
    ).move_to(soma_pos)
    nucleus = Circle(
        radius=0.18, fill_color="#007799", fill_opacity=0.8, stroke_width=0
    ).move_to(soma_pos)

    # ── Axon ──
    axon_start = soma_pos + RIGHT * 0.45
    axon_end = np.array([x_offset + 3.0, 0, 0])
    axon = Line(axon_start, axon_end, stroke_color=color, stroke_width=2)

    # ── Myelin sheaths ──
    myelin = VGroup()
    for i in range(7):
        t = (i + 0.5) / 7
        pos = axon_start + (axon_end - axon_start) * t
        seg = RoundedRectangle(
            width=0.42, height=0.22, corner_radius=0.08,
            fill_color=color, fill_opacity=0.3,
            stroke_color=color, stroke_width=1.5
        ).move_to(pos)
        myelin.add(seg)

    # ── Neuromuscular junction ──
    junc_pos = axon_end + RIGHT * 0.25
    junction = VGroup(*[
        Dot(junc_pos + UP * dy, radius=0.05, color=AMBER)
        for dy in [-0.12, 0, 0.12]
    ])

    # ── Muscle fiber ──
    muscle_pos = junc_pos + RIGHT * 0.7
    muscle = RoundedRectangle(
        width=1.0, height=0.65, corner_radius=0.12,
        fill_color=MUSCLE_CLR, fill_opacity=0.65,
        stroke_color=AMBER, stroke_width=2
    ).move_to(muscle_pos)
    muscle_label = Text("Muscle", font_size=14, color=WHITE).move_to(muscle_pos)

    # ── Assemble ──
    group = VGroup(dendrites, soma, nucleus, axon, myelin, junction, muscle, muscle_label)

    return {
        "group": group,
        "dendrites": dendrites,
        "soma": soma,
        "nucleus": nucleus,
        "axon": axon,
        "myelin": myelin,
        "junction": junction,
        "muscle": muscle,
        "muscle_label": muscle_label,
        "soma_pos": soma_pos,
        "axon_start": axon_start,
        "axon_end": axon_end,
        "muscle_pos": muscle_pos,
        "junc_pos": junc_pos,
    }


class MotorNeuronALS(Scene):
    """Complete ALS motor neuron educational animation (~50s)."""

    def construct(self):
        self.camera.background_color = DARK_BG
        self.show_title()
        neuron = self.show_healthy_neuron()
        self.show_healthy_signal(neuron)
        self.show_als_progression(neuron)
        self.show_final_message()

    # ────────────────────────────────────────
    def show_title(self):
        title = Text(
            "Motor Neuron Signal Pathway",
            font_size=38, color=WHITE, weight=BOLD
        )
        subtitle = Text(
            "How ALS Disrupts the Brain–Muscle Connection",
            font_size=22, color=TEAL
        )
        subtitle.next_to(title, DOWN, buff=0.35)

        self.play(Write(title, run_time=1.2))
        self.play(FadeIn(subtitle, shift=UP * 0.15))
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle))

    # ────────────────────────────────────────
    def show_healthy_neuron(self):
        header = Text("Healthy Motor Neuron", font_size=26, color=TEAL, weight=BOLD)
        header.to_edge(UP, buff=0.4)
        self.play(Write(header, run_time=0.6))

        n = create_neuron_group(color=TEAL)

        # Animate construction
        self.play(GrowFromCenter(n["soma"], run_time=0.5), FadeIn(n["nucleus"]))
        self.play(
            *[Create(d, run_time=0.4) for d in n["dendrites"]],
            lag_ratio=0.08
        )
        self.play(Create(n["axon"], run_time=0.8))
        self.play(
            *[FadeIn(s, scale=0.5) for s in n["myelin"]],
            lag_ratio=0.06, run_time=0.6
        )
        self.play(FadeIn(n["junction"]), FadeIn(n["muscle"]), FadeIn(n["muscle_label"]))

        # Labels
        labels = VGroup()
        lbl_data = [
            ("Dendrites", n["dendrites"], UP, 0.2),
            ("Cell Body (Soma)", n["soma"], DOWN, 0.3),
            ("Axon", n["axon"], DOWN, 0.25),
            ("Myelin Sheath", n["myelin"][3], UP, 0.2),
            ("Synapse", n["junction"], DOWN, 0.25),
        ]
        for text, ref, direction, buff_val in lbl_data:
            lbl = Text(text, font_size=13, color=ManimColor(TEAL)).next_to(ref, direction, buff=buff_val)
            labels.add(lbl)
        self.play(*[FadeIn(l, shift=UP * 0.08) for l in labels], lag_ratio=0.1, run_time=0.8)
        self.wait(0.5)

        n["header"] = header
        n["labels"] = labels
        return n

    # ────────────────────────────────────────
    def show_healthy_signal(self, n):
        desc = Text(
            "Signal travels rapidly along myelinated axon → muscle contracts",
            font_size=16, color=ManimColor(MUTED)
        ).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(desc))

        # Signal pulse
        pulse = Dot(radius=0.14, color=AMBER)
        glow = Dot(radius=0.35, color=AMBER, fill_opacity=0.25)
        signal = VGroup(glow, pulse).move_to(n["soma_pos"])

        path = VMobject()
        path.set_points_as_corners([
            n["soma_pos"], n["axon_start"],
            n["axon_end"], n["junc_pos"], n["muscle_pos"]
        ])

        self.play(FadeIn(signal, scale=0.3))
        self.play(MoveAlongPath(signal, path, run_time=1.8, rate_func=smooth))

        # Muscle contraction
        self.play(
            n["muscle"].animate.scale(1.18).set_fill(color="#ffcc00", opacity=0.9),
            Flash(n["muscle"], color=AMBER, num_lines=8, line_length=0.3, run_time=0.3),
            run_time=0.25
        )
        self.play(
            n["muscle"].animate.scale(1 / 1.18).set_fill(color=MUSCLE_CLR, opacity=0.65),
            run_time=0.25
        )
        self.play(FadeOut(signal))
        self.wait(0.8)
        self.play(FadeOut(desc))

    # ────────────────────────────────────────
    def show_als_progression(self, n):
        # Transition
        self.play(FadeOut(n["header"]), FadeOut(n["labels"]))
        als_header = Text("ALS Progression", font_size=26, color=ALS_ORANGE, weight=BOLD)
        als_header.to_edge(UP, buff=0.4)
        self.play(Write(als_header, run_time=0.6))

        stages = [
            {
                "title": "Stage 1 — Early Signs",
                "desc": "Some dendrites retract · Signal slightly delayed",
                "color": AMBER,
            },
            {
                "title": "Stage 2 — Myelin Breakdown",
                "desc": "Myelin sheath degrades · Signal slows dramatically",
                "color": ALS_ORANGE,
            },
            {
                "title": "Stage 3 — Connection Lost",
                "desc": "Axon fragments · Muscle begins to atrophy · Signal blocked",
                "color": ALS_RED,
            },
        ]

        for i, stage in enumerate(stages):
            # Stage label
            stg_title = Text(stage["title"], font_size=18, color=stage["color"], weight=BOLD)
            stg_title.to_edge(DOWN, buff=0.8)
            stg_desc = Text(stage["desc"], font_size=14, color=ManimColor(MUTED))
            stg_desc.next_to(stg_title, DOWN, buff=0.15)
            self.play(FadeIn(stg_title), FadeIn(stg_desc), run_time=0.4)

            if i == 0:  # Early: dendrites fade, soma discolors
                self.play(
                    *[d.animate.set_stroke(opacity=0.15) for d in list(n["dendrites"])[4:]],
                    *[d.animate.set_stroke(color=ALS_ORANGE, opacity=0.5)
                      for d in list(n["dendrites"])[:4]],
                    n["soma"].animate.set_fill(color="#664422", opacity=0.85)
                        .set_stroke(color=ALS_ORANGE),
                    run_time=1.5
                )
                # Slow signal
                pulse = Dot(radius=0.1, color=ALS_ORANGE).move_to(n["soma_pos"])
                path = VMobject()
                path.set_points_as_corners([
                    n["soma_pos"], n["axon_start"], n["axon_end"],
                    n["junc_pos"], n["muscle_pos"]
                ])
                self.play(FadeIn(pulse))
                self.play(MoveAlongPath(pulse, path, run_time=3, rate_func=linear))
                self.play(
                    n["muscle"].animate.scale(1.06).set_fill(opacity=0.5),
                    run_time=0.2
                )
                self.play(
                    n["muscle"].animate.scale(1 / 1.06),
                    run_time=0.2
                )
                self.play(FadeOut(pulse))

            elif i == 1:  # Mid: myelin breaks, axon changes
                self.play(
                    *[s.animate.set_fill(opacity=0).set_stroke(opacity=0.15)
                      for s in list(n["myelin"])[3:]],
                    *[s.animate.set_fill(opacity=0.1).set_stroke(opacity=0.4)
                      for s in list(n["myelin"])[:3]],
                    n["axon"].animate.set_stroke(color=ALS_ORANGE, opacity=0.5),
                    run_time=1.5
                )
                # Signal that dies halfway
                mid_point = (n["axon_start"] + n["axon_end"]) / 2
                pulse = Dot(radius=0.1, color=ALS_ORANGE).move_to(n["soma_pos"])
                half_path = VMobject()
                half_path.set_points_as_corners([n["soma_pos"], n["axon_start"], mid_point])
                self.play(FadeIn(pulse))
                self.play(MoveAlongPath(pulse, half_path, run_time=2.5, rate_func=linear))
                self.play(pulse.animate.set_opacity(0), run_time=0.4)
                self.remove(pulse)

            elif i == 2:  # Advanced: total breakdown
                self.play(
                    n["axon"].animate.set_stroke(opacity=0.15, color=ALS_DARK),
                    *[s.animate.set_fill(opacity=0).set_stroke(opacity=0)
                      for s in n["myelin"]],
                    n["junction"].animate.set_opacity(0.15),
                    n["muscle"].animate.set_fill(color="#884444", opacity=0.25).scale(0.8),
                    n["muscle_label"].animate.set_opacity(0.3),
                    n["dendrites"].animate.set_stroke(opacity=0.08),
                    n["soma"].animate.set_fill(color=ALS_DARK, opacity=0.4).scale(0.85),
                    n["nucleus"].animate.set_opacity(0.3),
                    run_time=2
                )
                # X block marker
                block_pos = n["axon_start"] + (n["axon_end"] - n["axon_start"]) * 0.35
                cross = Cross(stroke_color=ALS_RED, stroke_width=4).scale(0.25).move_to(block_pos)
                block_lbl = Text("BLOCKED", font_size=12, color=ALS_RED)
                block_lbl.next_to(cross, DOWN, buff=0.12)
                self.play(Create(cross, run_time=0.4), FadeIn(block_lbl))

            self.wait(1.2)
            self.play(FadeOut(stg_title), FadeOut(stg_desc), run_time=0.3)

        self.play(FadeOut(als_header))

    # ────────────────────────────────────────
    def show_final_message(self):
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

        msg1 = Text(
            "ALS progressively destroys motor neurons",
            font_size=24, color=WHITE
        )
        msg2 = Text(
            "severing the brain–muscle connection",
            font_size=24, color=ManimColor(TEAL)
        )
        msg2.next_to(msg1, DOWN, buff=0.3)

        hope = Text(
            "Research continues worldwide to find treatments and a cure",
            font_size=16, color=ManimColor(MUTED)
        )
        hope.next_to(msg2, DOWN, buff=0.6)

        self.play(FadeIn(msg1, shift=UP * 0.2), run_time=0.8)
        self.play(FadeIn(msg2, shift=UP * 0.15), run_time=0.6)
        self.play(FadeIn(hope, shift=UP * 0.1), run_time=0.5)
        self.wait(3)
        self.play(FadeOut(msg1), FadeOut(msg2), FadeOut(hope))


class MotorNeuronComparison(Scene):
    """Side-by-side healthy vs ALS comparison (~20s)."""

    def construct(self):
        self.camera.background_color = DARK_BG

        title = Text("Healthy vs ALS-Affected Neuron", font_size=30, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.35)
        self.play(Write(title, run_time=0.8))

        # Divider line
        divider = DashedLine(UP * 2.5, DOWN * 2.5, color=PURPLE, dash_length=0.15)
        self.play(Create(divider, run_time=0.4))

        # Labels
        h_lbl = Text("Healthy", font_size=20, color=TEAL, weight=BOLD)
        h_lbl.move_to(UP * 2.2 + LEFT * 3)
        a_lbl = Text("ALS-Affected", font_size=20, color=ALS_ORANGE, weight=BOLD)
        a_lbl.move_to(UP * 2.2 + RIGHT * 3)
        self.play(FadeIn(h_lbl), FadeIn(a_lbl))

        # Build two neurons
        healthy = create_neuron_group(x_offset=-3, color=TEAL)
        als_n = create_neuron_group(x_offset=3, color=ALS_ORANGE)

        # Scale to fit
        healthy["group"].scale(0.55).shift(LEFT * 0.3)
        als_n["group"].scale(0.55).shift(RIGHT * 0.3)

        self.play(FadeIn(healthy["group"]), FadeIn(als_n["group"]))

        # Degrade ALS neuron
        self.play(
            *[d.animate.set_stroke(opacity=0.15) for d in list(als_n["dendrites"])[3:]],
            als_n["soma"].animate.set_fill(color=ALS_DARK, opacity=0.5),
            als_n["axon"].animate.set_stroke(opacity=0.3, color=ALS_DARK),
            *[s.animate.set_fill(opacity=0).set_stroke(opacity=0.1) for s in list(als_n["myelin"])[2:]],
            als_n["muscle"].animate.set_fill(color="#884444", opacity=0.3).scale(0.8),
            als_n["junction"].animate.set_opacity(0.2),
            run_time=2
        )

        # Send signals simultaneously
        h_pulse = Dot(radius=0.08, color=AMBER)
        a_pulse = Dot(radius=0.08, color=ALS_ORANGE)

        h_path = VMobject()
        h_path.set_points_as_corners([
            healthy["soma_pos"] * 0.55 + LEFT * 0.3,
            healthy["muscle_pos"] * 0.55 + LEFT * 0.3
        ])
        a_path = VMobject()
        a_mid = (als_n["axon_start"] + als_n["axon_end"]) / 2
        a_path.set_points_as_corners([
            als_n["soma_pos"] * 0.55 + RIGHT * 0.3,
            a_mid * 0.55 + RIGHT * 0.3
        ])

        h_pulse.move_to(h_path.get_start())
        a_pulse.move_to(a_path.get_start())
        self.play(FadeIn(h_pulse), FadeIn(a_pulse))

        self.play(
            MoveAlongPath(h_pulse, h_path, run_time=1.5, rate_func=smooth),
            MoveAlongPath(a_pulse, a_path, run_time=2.5, rate_func=linear),
        )

        # Healthy muscle contracts
        check = Text("✓", font_size=24, color=TEAL)
        check.next_to(healthy["muscle"], RIGHT, buff=0.15).scale(0.55).shift(LEFT * 0.3)
        cross = Text("✗", font_size=24, color=ALS_RED)
        cross.next_to(als_n["muscle"], RIGHT, buff=0.15).scale(0.55).shift(RIGHT * 0.3)

        self.play(
            FadeIn(check, scale=1.5),
            a_pulse.animate.set_opacity(0),
            run_time=0.4
        )
        self.play(FadeIn(cross, scale=1.5), run_time=0.4)
        self.play(FadeOut(h_pulse))

        self.wait(3)
        self.play(*[FadeOut(m) for m in self.mobjects])
