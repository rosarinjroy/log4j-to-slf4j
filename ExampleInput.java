public class ExampleInput {

    public static void main(String[] args) {
        // Simple input.
        logger.info("Hello {}", who);

        // Variable between two strings.
        logger.info("Hello {} there", who);

        // Simple function call.
        logger.info("Hello {}", getWho());

        // Function call between two strings.
        logger.info("Hello {} there", getWho());

        // Complex variable list.
        logger.info("Hello {}, {}!", who, greeting);

        // Multiple input lines.
        logger.info("hello  there{}", who);

        // No leading spaces.
logger.info("Hello {}", who);

        // Logger name is log
        log.info("Hello {}", who);

        // No arguments at all, just a constant string.
        logger.info("Hello World!");

        // Function call with its own arguments.
        logger.info("Hello {}", greetWho(today()));

        // Function call with complex arguments. The input will be the same as output.
        logger.info("Hello " + greetWho("wo" + "r" + "ld"));
    }
}
