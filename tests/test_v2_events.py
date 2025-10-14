"""
Tests for event-driven architecture.
"""

import pytest
import asyncio

from src.accelerapp.core.events import (
    Event,
    EventBus,
    EventHandler,
    AsyncEventHandler,
    EventStore,
    EventStream,
    Saga,
    SagaState,
    SagaOrchestrator,
)


class TestEvent:
    """Test Event class."""
    
    def test_event_creation(self):
        """Test creating an event."""
        event = Event(
            event_type="test.event",
            data={"key": "value"},
            source="test_source"
        )
        
        assert event.event_type == "test.event"
        assert event.data == {"key": "value"}
        assert event.source == "test_source"
        assert event.event_id is not None
        assert event.timestamp is not None
    
    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        event = Event(
            event_type="test.event",
            data={"key": "value"}
        )
        
        event_dict = event.to_dict()
        
        assert event_dict["event_type"] == "test.event"
        assert event_dict["data"] == {"key": "value"}
        assert "event_id" in event_dict
        assert "timestamp" in event_dict


@pytest.mark.asyncio
class TestEventBus:
    """Test EventBus functionality."""
    
    async def test_subscribe_and_publish(self):
        """Test subscribing and publishing events."""
        bus = EventBus()
        received_events = []
        
        def handler(event: Event):
            received_events.append(event)
        
        bus.subscribe("test.event", handler)
        
        event = Event(event_type="test.event", data={"test": "data"})
        await bus.publish(event)
        
        # Start processing
        await bus.start_processing()
        await asyncio.sleep(0.1)  # Give time to process
        await bus.stop_processing()
        
        assert len(received_events) == 1
        assert received_events[0].event_type == "test.event"
    
    async def test_multiple_subscribers(self):
        """Test multiple subscribers for same event type."""
        bus = EventBus()
        received_1 = []
        received_2 = []
        
        def handler1(event: Event):
            received_1.append(event)
        
        def handler2(event: Event):
            received_2.append(event)
        
        bus.subscribe("test.event", handler1)
        bus.subscribe("test.event", handler2)
        
        event = Event(event_type="test.event")
        await bus.publish(event)
        
        await bus.start_processing()
        await asyncio.sleep(0.1)
        await bus.stop_processing()
        
        assert len(received_1) == 1
        assert len(received_2) == 1
    
    async def test_async_handler(self):
        """Test async event handlers."""
        bus = EventBus()
        received_events = []
        
        async def async_handler(event: Event):
            await asyncio.sleep(0.01)
            received_events.append(event)
        
        bus.subscribe("test.event", async_handler)
        
        event = Event(event_type="test.event")
        await bus.publish(event)
        
        await bus.start_processing()
        await asyncio.sleep(0.1)
        await bus.stop_processing()
        
        assert len(received_events) == 1
    
    async def test_unsubscribe(self):
        """Test unsubscribing from events."""
        bus = EventBus()
        received_events = []
        
        def handler(event: Event):
            received_events.append(event)
        
        bus.subscribe("test.event", handler)
        bus.unsubscribe("test.event", handler)
        
        event = Event(event_type="test.event")
        await bus.publish(event)
        
        await bus.start_processing()
        await asyncio.sleep(0.1)
        await bus.stop_processing()
        
        assert len(received_events) == 0
    
    async def test_dead_letter_queue(self):
        """Test dead letter queue for failed events."""
        bus = EventBus()
        
        def failing_handler(event: Event):
            raise ValueError("Handler failed")
        
        bus.subscribe("test.event", failing_handler)
        
        event = Event(event_type="test.event")
        await bus.publish(event)
        
        await bus.start_processing()
        await asyncio.sleep(0.1)
        await bus.stop_processing()
        
        dlq = bus.get_dead_letter_queue()
        assert len(dlq) > 0
    
    async def test_event_history(self):
        """Test event history tracking."""
        bus = EventBus()
        
        def handler(event: Event):
            pass
        
        bus.subscribe("test.event", handler)
        
        event1 = Event(event_type="test.event", data={"id": 1})
        event2 = Event(event_type="test.event", data={"id": 2})
        
        await bus.publish(event1)
        await bus.publish(event2)
        
        await bus.start_processing()
        await asyncio.sleep(0.1)
        await bus.stop_processing()
        
        history = bus.get_event_history(limit=10)
        assert len(history) == 2
    
    async def test_get_stats(self):
        """Test getting event bus statistics."""
        bus = EventBus()
        
        def handler(event: Event):
            pass
        
        bus.subscribe("test.event", handler)
        
        stats = bus.get_stats()
        
        assert "queue_size" in stats
        assert "total_subscribers" in stats
        assert stats["total_subscribers"] == 1


@pytest.mark.asyncio
class TestEventStore:
    """Test EventStore functionality."""
    
    async def test_append_event(self):
        """Test appending events to store."""
        store = EventStore()
        
        event = Event(event_type="test.event", data={"key": "value"})
        await store.append(event)
        
        assert store.get_event_count() == 1
    
    async def test_get_events_by_type(self):
        """Test filtering events by type."""
        store = EventStore()
        
        event1 = Event(event_type="type1")
        event2 = Event(event_type="type2")
        event3 = Event(event_type="type1")
        
        await store.append(event1)
        await store.append(event2)
        await store.append(event3)
        
        type1_events = await store.get_events(event_type="type1")
        assert len(type1_events) == 2
    
    async def test_get_events_by_aggregate_id(self):
        """Test filtering events by aggregate ID."""
        store = EventStore()
        
        event1 = Event(event_type="test", data={"aggregate_id": "agg1"})
        event2 = Event(event_type="test", data={"aggregate_id": "agg2"})
        event3 = Event(event_type="test", data={"aggregate_id": "agg1"})
        
        await store.append(event1)
        await store.append(event2)
        await store.append(event3)
        
        agg1_events = await store.get_events(aggregate_id="agg1")
        assert len(agg1_events) == 2
    
    async def test_replay_events(self):
        """Test replaying events."""
        store = EventStore()
        
        event1 = Event(event_type="test", data={"value": 1})
        event2 = Event(event_type="test", data={"value": 2})
        
        await store.append(event1)
        await store.append(event2)
        
        replayed = []
        
        def handler(event):
            replayed.append(event.data["value"])
        
        await store.replay(handler)
        
        assert replayed == [1, 2]
    
    async def test_snapshot_creation(self):
        """Test creating and retrieving snapshots."""
        store = EventStore()
        
        state = {"counter": 10}
        await store.create_snapshot("agg1", state)
        
        snapshot = await store.get_snapshot("agg1")
        assert snapshot is not None
        assert snapshot["state"] == state


@pytest.mark.asyncio
class TestEventStream:
    """Test EventStream functionality."""
    
    async def test_append_to_stream(self):
        """Test appending events to stream."""
        store = EventStore()
        stream = EventStream("agg1", store)
        
        event = Event(event_type="test")
        await stream.append_event(event)
        
        assert stream.version == 1
        assert store.get_event_count() == 1
    
    async def test_get_stream_events(self):
        """Test getting events for a stream."""
        store = EventStore()
        stream = EventStream("agg1", store)
        
        event1 = Event(event_type="test", data={"value": 1})
        event2 = Event(event_type="test", data={"value": 2})
        
        await stream.append_event(event1)
        await stream.append_event(event2)
        
        events = await stream.get_events()
        assert len(events) == 2
    
    async def test_rebuild_state(self):
        """Test rebuilding state from events."""
        store = EventStore()
        stream = EventStream("agg1", store)
        
        event1 = Event(event_type="increment", data={"amount": 5})
        event2 = Event(event_type="increment", data={"amount": 3})
        
        await stream.append_event(event1)
        await stream.append_event(event2)
        
        def reducer(state, event):
            if event.event_type == "increment":
                state["counter"] += event.data["amount"]
            return state
        
        initial_state = {"counter": 0}
        final_state = await stream.rebuild_state(initial_state, reducer)
        
        assert final_state["counter"] == 8


@pytest.mark.asyncio
class TestSaga:
    """Test Saga pattern."""
    
    async def test_saga_execution_success(self):
        """Test successful saga execution."""
        class TestSaga(Saga):
            pass
        
        saga = TestSaga("test_saga")
        results = []
        
        def step1(context):
            results.append("step1")
            return "result1"
        
        def step2(context):
            results.append("step2")
            return "result2"
        
        saga.add_step("step1", step1)
        saga.add_step("step2", step2)
        
        success = await saga.execute()
        
        assert success
        assert saga.state == SagaState.COMPLETED
        assert results == ["step1", "step2"]
    
    async def test_saga_compensation(self):
        """Test saga compensation on failure."""
        class TestSaga(Saga):
            pass
        
        saga = TestSaga("test_saga")
        compensations = []
        
        def step1(context):
            return "result1"
        
        def compensate1(context):
            compensations.append("compensate1")
        
        def step2(context):
            raise ValueError("Step2 failed")
        
        saga.add_step("step1", step1, compensate1)
        saga.add_step("step2", step2)
        
        success = await saga.execute()
        
        assert not success
        assert saga.state == SagaState.COMPENSATED
        assert "compensate1" in compensations
    
    async def test_saga_context(self):
        """Test saga context propagation."""
        class TestSaga(Saga):
            pass
        
        saga = TestSaga("test_saga")
        
        def step1(context):
            context["data"] = "from_step1"
            return "result1"
        
        def step2(context):
            assert context["data"] == "from_step1"
            return "result2"
        
        saga.add_step("step1", step1)
        saga.add_step("step2", step2)
        
        await saga.execute()
        
        context = saga.get_context()
        assert "step1" in context
        assert "step2" in context


@pytest.mark.asyncio
class TestSagaOrchestrator:
    """Test SagaOrchestrator functionality."""
    
    async def test_register_and_execute_saga(self):
        """Test registering and executing sagas."""
        orchestrator = SagaOrchestrator()
        
        class TestSaga(Saga):
            pass
        
        saga = TestSaga("test_saga")
        saga.add_step("step1", lambda ctx: "result")
        
        orchestrator.register_saga(saga)
        
        success = await orchestrator.execute_saga("test_saga")
        
        assert success
        assert orchestrator.get_saga_state("test_saga") == SagaState.COMPLETED
    
    async def test_orchestrator_with_event_bus(self):
        """Test orchestrator integration with event bus."""
        event_bus = EventBus()
        orchestrator = SagaOrchestrator(event_bus)
        
        class TestSaga(Saga):
            pass
        
        saga = TestSaga("test_saga")
        saga.add_step("step1", lambda ctx: "result")
        
        orchestrator.register_saga(saga)
        
        # Start event processing
        await event_bus.start_processing()
        
        success = await orchestrator.execute_saga("test_saga")
        
        await asyncio.sleep(0.1)
        await event_bus.stop_processing()
        
        assert success
        
        # Check for saga events in history
        history = event_bus.get_event_history()
        saga_events = [e for e in history if "saga" in e.event_type]
        assert len(saga_events) > 0
