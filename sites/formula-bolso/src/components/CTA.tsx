import Link from 'next/link'

interface CTAProps {
  title: string
  description: string
  primaryText: string
  primaryLink: string
  secondaryText?: string
  secondaryLink?: string
}

export default function CTA({ title, description, primaryText, primaryLink, secondaryText, secondaryLink }: CTAProps) {
  return (
    <section className="py-20 px-4">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-4xl font-bold mb-4">{title}</h2>
        <p className="text-xl text-muted-foreground mb-8">{description}</p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href={primaryLink}
            target={primaryLink.startsWith('http') ? '_blank' : undefined}
            rel={primaryLink.startsWith('http') ? 'noopener noreferrer' : undefined}
            className="px-8 py-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-semibold text-lg"
          >
            {primaryText}
          </a>
          {secondaryText && secondaryLink && (
            <Link
              href={secondaryLink}
              className="px-8 py-4 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors font-semibold text-lg border border-white/20"
            >
              {secondaryText}
            </Link>
          )}
        </div>
      </div>
    </section>
  )
}

