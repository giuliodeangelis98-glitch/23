#!/usr/bin/env python3
"""Generate plausible excuses for late commits. Bilingual (en/es)."""
from __future__ import annotations

import argparse
import random
import subprocess
from collections import Counter

TEMPLATES = {
    "en": [
        "{actor} pushed a force-rebase right before I could commit, so I had to rebuild the {thing} from scratch.",
        "{actor} merged a breaking change to the {thing} that took down our entire CI pipeline.",
        "Our {thing} dependency got yanked from npm and {actor} had to vendor it manually.",
        "I was 90% done but {actor}'s migration on the {thing} required a full schema rewrite.",
        "The {thing} flake came back and {actor} and I spent the day bisecting it.",
        "VPN was down, the office Wi-Fi died, and {actor} broke the {thing} on top of that.",
        "{actor} accidentally deleted staging's {thing}, recovery took priority.",
        "A cosmic ray flipped a bit in the {thing} cache. {actor} can corroborate.",
        "{actor} scheduled a 4-hour meeting about {thing} naming conventions.",
        "The {thing} tests started failing only on Tuesdays. {actor} is investigating.",
    ],
    "es": [
        "{actor} hizo un force-push justo cuando iba a commitear y tuve que rehacer {thing} desde cero.",
        "{actor} fusionó un cambio que rompió {thing} y se cayó todo el CI.",
        "La dependencia de {thing} desapareció de npm y {actor} tuvo que vendorearla a mano.",
        "Estaba al 90% pero la migración de {actor} sobre {thing} pidió reescribir el esquema entero.",
        "Volvió el flake de {thing} y {actor} y yo nos pasamos el día haciendo bisect.",
        "Se cayó el VPN, se cayó el wifi y encima {actor} rompió {thing}.",
        "{actor} borró sin querer {thing} de staging y la recuperación fue prioridad.",
        "Un rayo cósmico volteó un bit en el caché de {thing}. {actor} puede confirmarlo.",
        "{actor} agendó una reunión de cuatro horas sobre cómo nombrar {thing}.",
        "Los tests de {thing} empezaron a fallar solo los martes. {actor} sigue investigando.",
    ],
}

THINGS = [
    "auth flow", "build cache", "prod database", "feature flag service",
    "websocket layer", "migrations folder", "Docker base image", "test fixtures",
    "staging cluster", "rate limiter", "PDF renderer", "legacy cron jobs",
]
THINGS_ES = [
    "el flujo de auth", "el caché de build", "la base de datos de producción",
    "el servicio de feature flags", "la capa de websockets", "la carpeta de migraciones",
    "la imagen base de Docker", "los fixtures de tests", "el cluster de staging",
    "el rate limiter", "el renderizador de PDFs", "los cron jobs legados",
]
GENERIC_ACTORS = ["a colleague", "an intern", "the platform team", "DevOps", "a contractor"]
GENERIC_ACTORS_ES = ["un colega", "un intern", "el equipo de plataforma", "DevOps", "un contractor"]


def git_authors(limit: int = 200) -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", "log", f"-n{limit}", "--pretty=format:%an"],
            text=True, stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    names = [n for n in (line.strip() for line in out.splitlines()) if n]
    if not names:
        return []
    counts = Counter(names)
    try:
        me = subprocess.check_output(
            ["git", "config", "user.name"], text=True, stderr=subprocess.DEVNULL,
        ).strip()
        counts.pop(me, None)
    except subprocess.CalledProcessError:
        pass
    return [name for name, _ in counts.most_common()]


def pick_actor(blame_git: bool, lang: str) -> str:
    if blame_git:
        authors = git_authors()
        if authors:
            return random.choice(authors)
    pool = GENERIC_ACTORS_ES if lang == "es" else GENERIC_ACTORS
    return random.choice(pool)


def generate(lang: str, blame_git: bool, count: int) -> list[str]:
    things = THINGS_ES if lang == "es" else THINGS
    out = []
    for _ in range(count):
        template = random.choice(TEMPLATES[lang])
        out.append(template.format(actor=pick_actor(blame_git, lang), thing=random.choice(things)))
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Late-commit excuse generator")
    p.add_argument("--lang", choices=["en", "es"], default="en")
    p.add_argument("--blame", choices=["random", "git"], default="random",
                   help="random uses generic roles; git pulls real coauthors from git log")
    p.add_argument("-n", "--count", type=int, default=1)
    args = p.parse_args()
    for excuse in generate(args.lang, args.blame == "git", args.count):
        print(f"• {excuse}")


if __name__ == "__main__":
    main()
