<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xs="http://www.w3.org/2001/XMLSchema"
                exclude-result-prefixes="xs"
                version="2.0">
    <xsl:output indent="yes"/>
    <xsl:param name="hId" as="xs:string" required="yes"/>
    <xsl:param name="outlineUrn" as="xs:string" required="no"/>
    <xsl:param name="printMasterUrn" as="xs:string" required="no"/>
    <xsl:template match="property[@name='alephID']">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:attribute name="value">
                <xsl:value-of select="$hId"/>
            </xsl:attribute>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="property[@name='harvardMetadataLinks']">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:attribute name="value">
                <xsl:value-of select="replace(@value, 'hollis-id', $hId)"/>
            </xsl:attribute>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="metadataCategory[@name='objectMetadata']">
        <xsl:copy>
            <xsl:copy-of select="@*|node()"/>
            <xsl:if test="$printMasterUrn != '' ">
                <!--<xsl:message>-->
                  <!--pm: <xsl:value-of select="$printMasterUrn"/>-->
                <!--</xsl:message>-->
                <property name="relatedLinks" value="Relationship=Print Master --- URI={$printMasterUrn}"/>
            </xsl:if>
            <xsl:if test="$outlineUrn != '' ">
                  <!--<xsl:message>-->
                        <!--o: <xsl:value-of select="$outlineUrn"/>-->
                    <!--</xsl:message>-->
                <property name="relatedLinks" value="Relationship=Outline --- URI={$outlineUrn}"/>
            </xsl:if>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="@*|node()">
        <xsl:copy>
                <!--<xsl:message><xsl:value-of select="."></xsl:value-of></xsl:message>-->
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>