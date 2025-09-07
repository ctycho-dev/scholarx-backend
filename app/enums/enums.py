from enum import Enum


class AppMode(str, Enum):
    """App mode."""

    PROD = "prod"
    DEV = "dev"
    TEST = "test"


class UserRole(str, Enum):
    """Enum representing possible user roles in the system.

    Attributes:
        ADMIN: Administrator role with full privileges.
        BD: Business Development role with specific privileges.
        USER: Regular user role with basic privileges.
    """
    ADMIN = "admin"
    BD = "bd"
    USER = 'user'


class WalletChains(str, Enum):
    """Enum representing supported blockchain networks for wallets.

    Attributes:
        ETH: Ethereum blockchain.
        SOL: Solana blockchain.
    """
    ETH = "eth"
    SOL = "sol"


class AuthProvider(str, Enum):
    """Enum representing authentication providers supported by the system.

    Attributes:
        GOOGLE: Google OAuth provider.
        DISCORD: Discord OAuth provider.
        TWITTER: Twitter OAuth provider.
        EMAIL: Email-based authentication.
    """
    GOOGLE = "google_oauth"
    DISCORD = "discord_oauth"
    GITHUB = "github_oauth"
    TWITTER = "twitter_oauth"
    EMAIL = "email"
    WALLET = "wallet"


class ReportState(str, Enum):
    """Enum representing the possible states of a report."""

    SUBMITTED = 'submitted'
    CHECKING = 'checking'
    WRITING = 'writing'
    UPDATE_INFO = 'update_info'
    COMPLETED = 'completed'
    REJECTED = 'rejected'


class ArticleState(str, Enum):

    DRAFT = "Draft"
    PUBLISHED = "Published"
    ARCHIVED = "Archived"


class ImageType(str, Enum):

    ARTICLE = "article"
    PROFILE = "profile"


class ImageStatus(str, Enum):

    CREATED = "created"
    STORED = "stored"
    PUBLISHED = "published"