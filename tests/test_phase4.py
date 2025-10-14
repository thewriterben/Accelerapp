"""
Tests for Phase 4: Community Ecosystem and Production Launch.
"""

import pytest
from accelerapp.community.portal.forums import ForumManager, ForumPost
from accelerapp.community.portal.tutorials import TutorialManager, DifficultyLevel
from accelerapp.community.portal.showcase import ProjectShowcase
from accelerapp.community.governance.contributor_guide import ContributorGuide
from accelerapp.community.onboarding.developer_setup import DeveloperOnboarding
from accelerapp.community.marketplace_web.api import MarketplaceAPI
from accelerapp.integrations.ci_cd.github_actions import GitHubActionsIntegration
from accelerapp.integrations.ci_cd.jenkins import JenkinsIntegration
from accelerapp.integrations.cloud_platforms.aws import AWSIntegration
from accelerapp.integrations.cloud_platforms.azure import AzureIntegration
from accelerapp.integrations.hardware_vendors.arduino import ArduinoIDEIntegration
from accelerapp.integrations.development_tools.vscode import VSCodeExtension
from accelerapp.production.benchmarking.performance_tests import PerformanceBenchmark
from accelerapp.production.security.vulnerability_scan import (
    VulnerabilityScanner,
    Severity,
)
from accelerapp.production.deployment.automation import (
    DeploymentAutomation,
    DeploymentStatus,
)
from accelerapp.production.support.troubleshooting import TroubleshootingGuide
from accelerapp.business.analytics.usage_tracking import UsageAnalytics
from accelerapp.business.monetization.premium_features import (
    PremiumFeatureManager,
    SubscriptionTier,
)
from accelerapp.business.partnerships.vendor_program import (
    PartnershipManager,
    PartnerType,
    PartnerTier,
)
from accelerapp.business.marketing.content_strategy import (
    ContentManager,
    ContentType,
    ContentStatus,
)


# Community Portal Tests
def test_forum_manager_creation():
    """Test forum manager creation and post management."""
    forum = ForumManager()
    assert len(forum.categories) > 0

    post = forum.create_post(
        "post1",
        "General Discussion",
        "Welcome to Accelerapp",
        "admin",
        "This is the first post",
        tags=["welcome"],
    )

    assert post.id == "post1"
    assert post.title == "Welcome to Accelerapp"
    assert len(forum.posts) == 1


def test_forum_replies():
    """Test forum reply system."""
    forum = ForumManager()
    post = forum.create_post("post1", "General Discussion", "Test", "user1", "Content")

    reply = forum.add_reply("post1", "reply1", "user2", "Great post!")
    assert reply.id == "reply1"
    assert len(forum.posts["post1"].replies) == 1


def test_forum_statistics():
    """Test forum statistics."""
    forum = ForumManager()
    forum.create_post("post1", "General Discussion", "Test 1", "user1", "Content 1")
    forum.create_post("post2", "Hardware Support", "Test 2", "user2", "Content 2")
    forum.add_reply("post1", "reply1", "user3", "Reply")

    stats = forum.get_statistics()
    assert stats["total_posts"] == 2
    assert stats["total_replies"] == 1
    assert stats["total_interactions"] == 3


def test_tutorial_manager():
    """Test tutorial manager."""
    manager = TutorialManager()

    tutorial = manager.create_tutorial(
        "tut1",
        "Getting Started",
        "Learn the basics",
        "instructor",
        DifficultyLevel.BEGINNER,
        "basics",
        30,
    )

    assert tutorial.id == "tut1"
    assert tutorial.difficulty == DifficultyLevel.BEGINNER

    manager.add_step("tut1", 1, "Install", "Install dependencies", "pip install accelerapp")
    assert len(manager.tutorials["tut1"].steps) == 1


def test_tutorial_progress():
    """Test tutorial progress tracking."""
    manager = TutorialManager()
    manager.create_tutorial(
        "tut1", "Test", "Description", "author", DifficultyLevel.BEGINNER, "test", 30
    )
    manager.add_step("tut1", 1, "Step 1", "First step")
    manager.add_step("tut1", 2, "Step 2", "Second step")

    manager.start_tutorial("user1", "tut1")
    progress = manager.get_progress("user1", "tut1")
    assert progress == 0

    manager.complete_step("user1", "tut1", 1)
    progress = manager.get_progress("user1", "tut1")
    assert progress == 1


def test_project_showcase():
    """Test project showcase."""
    showcase = ProjectShowcase()

    project = showcase.submit_project(
        "proj1",
        "LED Controller",
        "Control LEDs with Arduino",
        "maker1",
        "arduino",
        repository_url="https://github.com/user/project",
    )

    assert project.id == "proj1"
    assert project.hardware_platform == "arduino"

    showcase.like_project("proj1")
    assert showcase.projects["proj1"].likes == 1


def test_contributor_guide():
    """Test contributor guide."""
    guide = ContributorGuide()

    # Should have default guidelines
    assert len(guide.guidelines) > 0

    contributor = guide.register_contributor("user1", "John Doe", "john@example.com")
    assert contributor.username == "user1"

    guide.record_contribution("user1")
    assert guide.contributors["user1"].contributions == 1


def test_developer_onboarding():
    """Test developer onboarding."""
    onboarding = DeveloperOnboarding()

    profile = onboarding.create_profile("dev1", "dev@example.com", "beginner")
    assert profile.experience_level == "beginner"

    next_step = onboarding.get_next_step("dev1")
    assert next_step is not None
    assert next_step.number == 1

    onboarding.complete_step("dev1", 1)
    progress = onboarding.get_progress("dev1")
    assert progress["completed_steps"] == 1


def test_marketplace_api():
    """Test marketplace web API."""
    api = MarketplaceAPI()

    # Should integrate with registry
    stats = api.get_statistics()
    assert "total_templates" in stats


# Integrations Tests
def test_github_actions_integration():
    """Test GitHub Actions integration."""
    gh = GitHubActionsIntegration()

    workflow = gh.generate_ci_workflow("TestProject", ["arduino", "esp32"])
    assert "name: TestProject CI" in workflow
    assert "accelerapp generate" in workflow

    release_workflow = gh.generate_release_workflow("TestProject")
    assert "Release" in release_workflow


def test_jenkins_integration():
    """Test Jenkins integration."""
    jenkins = JenkinsIntegration()

    pipeline = jenkins.generate_pipeline("TestProject", ["arduino"])
    assert "pipeline {" in pipeline
    assert "arduino" in pipeline


def test_aws_integration():
    """Test AWS integration."""
    aws = AWSIntegration()

    lambda_config = aws.generate_lambda_deployment("test-function")
    assert "AWSTemplateFormatVersion" in lambda_config
    assert "Resources" in lambda_config

    iot_config = aws.generate_iot_core_integration("test-thing", ["arduino"])
    assert "IoTThing" in iot_config["Resources"]


def test_azure_integration():
    """Test Azure integration."""
    azure = AzureIntegration()

    function_config = azure.generate_function_app_config("test-app")
    assert "$schema" in function_config
    assert "resources" in function_config

    pipeline = azure.generate_devops_pipeline("TestProject", ["arduino"])
    assert "trigger:" in pipeline


def test_arduino_ide_integration():
    """Test Arduino IDE integration."""
    arduino = ArduinoIDEIntegration()

    properties = arduino.generate_library_properties(
        "TestLib", "1.0.0", "Author", "Test library"
    )
    assert "name=TestLib" in properties
    assert "version=1.0.0" in properties

    header = arduino.generate_library_header("TestLib")
    assert "#ifndef TESTLIB_H" in header
    assert "class TestLib" in header


def test_vscode_extension():
    """Test VS Code extension."""
    vscode = VSCodeExtension()

    manifest = vscode.generate_extension_manifest("accelerapp", "1.0.0", "Accelerapp extension")
    assert manifest["name"] == "accelerapp"
    assert "commands" in manifest["contributes"]

    snippets = vscode.generate_snippets()
    assert "Accelerapp Device Configuration" in snippets


# Production Tests
def test_performance_benchmark():
    """Test performance benchmarking."""
    benchmark = PerformanceBenchmark()

    def test_func():
        total = 0
        for i in range(100):
            total += i
        return total

    benchmark.register_benchmark("test_sum", test_func)
    result = benchmark.run_benchmark("test_sum", iterations=100)

    assert result.success
    assert result.operations_per_second > 0
    assert result.duration_ms > 0


def test_vulnerability_scanner():
    """Test vulnerability scanner."""
    scanner = VulnerabilityScanner()

    vuln = scanner.add_vulnerability(
        "vuln1",
        "Test Vulnerability",
        "Description",
        Severity.HIGH,
        "test-component",
        affected_versions=["1.0.0"],
    )

    assert vuln.id == "vuln1"
    assert vuln.severity == Severity.HIGH

    result = scanner.scan_dependencies(["test-component"])
    assert result.total_scanned == 1


def test_deployment_automation():
    """Test deployment automation."""
    deployment = DeploymentAutomation()

    dep = deployment.create_deployment("dep1", "kubernetes", "production", "1.0.0")
    assert dep.id == "dep1"
    assert dep.status == DeploymentStatus.PENDING

    success = deployment.deploy("dep1")
    assert success
    assert deployment.deployments["dep1"].status == DeploymentStatus.SUCCESS


def test_deployment_manifests():
    """Test deployment manifest generation."""
    deployment = DeploymentAutomation()

    k8s_manifest = deployment.generate_kubernetes_manifest("test-app", "1.0.0", replicas=3)
    assert "kind: Deployment" in k8s_manifest
    assert "replicas: 3" in k8s_manifest

    docker_compose = deployment.generate_docker_compose("test-app", "1.0.0")
    assert "version: '3.8'" in docker_compose


def test_troubleshooting_guide():
    """Test troubleshooting guide."""
    guide = TroubleshootingGuide()

    # Should have default issues
    assert len(guide.issues) > 0

    results = guide.search_issues("installation")
    assert len(results) > 0

    ticket = guide.create_ticket("ticket1", "user1", "Help needed", "Description")
    assert ticket.ticket_id == "ticket1"
    assert ticket.status == "open"

    guide.update_ticket_status("ticket1", "resolved")
    assert guide.tickets["ticket1"].status == "resolved"


# Business Tests
def test_usage_analytics():
    """Test usage analytics."""
    analytics = UsageAnalytics()

    event = analytics.track_event("user1", "code_generation")
    assert event.user_id == "user1"
    assert event.event_type == "code_generation"

    analytics.track_event("user1", "template_use")
    analytics.track_event("user2", "code_generation")

    metrics = analytics.get_user_metrics("user1")
    assert metrics.total_events == 2
    assert len(metrics.features_used) == 2

    stats = analytics.get_statistics()
    assert stats["unique_users"] == 2
    assert stats["total_events"] == 3


def test_premium_features():
    """Test premium feature management."""
    manager = PremiumFeatureManager()

    # Should have initialized features
    assert len(manager.features) > 0

    subscription = manager.create_subscription("user1", SubscriptionTier.PROFESSIONAL)
    assert subscription.user_id == "user1"
    assert subscription.tier == SubscriptionTier.PROFESSIONAL

    # Professional should have access to professional and lower tier features
    has_access = manager.check_feature_access("user1", "code-generation")
    assert has_access

    # Free user shouldn't have access to premium features
    has_access = manager.check_feature_access("user2", "ai-optimization")
    assert not has_access


def test_subscription_upgrade():
    """Test subscription upgrade."""
    manager = PremiumFeatureManager()

    manager.create_subscription("user1", SubscriptionTier.BASIC)
    assert manager.subscriptions["user1"].tier == SubscriptionTier.BASIC

    manager.upgrade_subscription("user1", SubscriptionTier.PROFESSIONAL)
    assert manager.subscriptions["user1"].tier == SubscriptionTier.PROFESSIONAL


def test_partnership_manager():
    """Test partnership management."""
    manager = PartnershipManager()

    # Should have default partners
    assert len(manager.partners) > 0

    partner = manager.register_partner(
        "test-partner",
        "Test Partner",
        PartnerType.TECHNOLOGY_PARTNER,
        PartnerTier.BRONZE,
        "partner@example.com",
    )

    assert partner.partner_id == "test-partner"
    assert partner.tier == PartnerTier.BRONZE

    manager.upgrade_partner_tier("test-partner", PartnerTier.SILVER)
    assert manager.partners["test-partner"].tier == PartnerTier.SILVER


def test_content_manager():
    """Test content management."""
    manager = ContentManager()

    # Should have sample content
    assert len(manager.content) > 0

    content = manager.create_content(
        "blog1", "New Blog Post", ContentType.BLOG_POST, "author1", "Summary", tags=["news"]
    )

    assert content.content_id == "blog1"
    assert content.status == ContentStatus.DRAFT

    manager.publish_content("blog1")
    assert manager.content["blog1"].status == ContentStatus.PUBLISHED


def test_content_tracking():
    """Test content tracking."""
    manager = ContentManager()

    manager.create_content(
        "blog1", "Test", ContentType.BLOG_POST, "author", "Summary"
    )
    manager.publish_content("blog1")

    # Get content increments views
    manager.get_content("blog1")
    assert manager.content["blog1"].views == 1

    manager.track_share("blog1")
    assert manager.content["blog1"].shares == 1


# Integration Tests
def test_community_ecosystem_integration():
    """Test community ecosystem integration."""
    forum = ForumManager()
    tutorials = TutorialManager()
    showcase = ProjectShowcase()

    # Create forum post about a tutorial
    post = forum.create_post(
        "post1",
        "Tutorials",
        "New Tutorial Available",
        "instructor",
        "Check out the new tutorial",
    )

    # Create tutorial
    tutorial = tutorials.create_tutorial(
        "tut1", "Advanced Features", "Desc", "instructor", DifficultyLevel.ADVANCED, "advanced", 60
    )

    # Add showcase project
    project = showcase.submit_project(
        "proj1", "Tutorial Example", "Example from tutorial", "user1", "arduino"
    )

    assert post.id == "post1"
    assert tutorial.id == "tut1"
    assert project.id == "proj1"


def test_production_pipeline_integration():
    """Test production pipeline integration."""
    benchmark = PerformanceBenchmark()
    scanner = VulnerabilityScanner()
    deployment = DeploymentAutomation()

    # Run benchmarks
    def dummy_benchmark():
        pass

    benchmark.register_benchmark("test", dummy_benchmark)
    bench_result = benchmark.run_benchmark("test", iterations=10)

    # Run security scan
    scan_result = scanner.scan_dependencies(["package1", "package2"])

    # Create deployment
    dep = deployment.create_deployment("dep1", "kubernetes", "production", "1.0.0")
    deployment.deploy("dep1")

    assert bench_result.success
    assert scan_result.total_scanned == 2
    assert deployment.deployments["dep1"].status == DeploymentStatus.SUCCESS


def test_business_metrics_integration():
    """Test business metrics integration."""
    analytics = UsageAnalytics()
    features = PremiumFeatureManager()
    partnerships = PartnershipManager()
    content = ContentManager()

    # Track usage
    analytics.track_event("user1", "code_generation")
    analytics.track_event("user1", "template_use")

    # Create subscription
    features.create_subscription("user1", SubscriptionTier.PROFESSIONAL)

    # Partner integration
    partner_count = len(partnerships.list_partners())

    # Content views
    published = content.list_content(status=ContentStatus.PUBLISHED)

    assert analytics.get_statistics()["total_events"] == 2
    assert features.check_feature_access("user1", "ai-optimization")
    assert partner_count > 0
    assert len(published) > 0
